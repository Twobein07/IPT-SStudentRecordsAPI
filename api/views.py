import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle

from .models import StudentRecord, PaymentRecord
from .serializers import (
    StudentRecordSerializer, StudentRecordWriteSerializer,
    PaymentRecordSerializer
)
from .permissions import IsAdminGroup, IsAdminOrFaculty, IsOwner, IsAdminOrReadOwn

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    rate = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login']
    scope = 'login'


@never_cache
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    throttle = LoginThrottle()
    if not throttle.allow_request(request, None):
        logger.warning("Rate limit hit for login from IP: %s", request.META.get('REMOTE_ADDR'))
        return Response(
            {"error": "Too many login attempts. Try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            logger.info("Login successful for user: %s", username)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': username,
                'role': list(user.groups.values_list('name', flat=True)),
            })
    except User.DoesNotExist:
        pass

    logger.warning("Failed login attempt for user: %s from IP: %s",
                   username, request.META.get('REMOTE_ADDR'))
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class StudentRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentRecord.objects.all()
    filterset_fields = ['course', 'year_level']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentRecordWriteSerializer
        return StudentRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Student').exists():
            return StudentRecord.objects.filter(owner=user)
        return StudentRecord.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminGroup]
        elif self.action in ['destroy']:
            permission_classes = [IsAdminGroup]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrFaculty]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        logger.info("Student record created by %s", self.request.user.username)

    def perform_update(self, serializer):
        serializer.save()
        logger.info("Student record updated by %s", self.request.user.username)

    def perform_destroy(self, instance):
        logger.warning("Student record deleted by %s: %s",
                       self.request.user.username, instance)
        instance.delete()


class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return PaymentRecord.objects.all()
        return PaymentRecord.objects.filter(owner=user)

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy']:
            permission_classes = [IsAdminGroup]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrFaculty]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrReadOwn]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        logger.info("Payment record created by %s", self.request.user.username)

    def perform_destroy(self, instance):
        logger.warning("Payment record deleted by %s: %s",
                       self.request.user.username, instance)
        instance.delete()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminGroup]

    def list(self, request, *args, **kwargs):
        users = User.objects.all().values('id', 'username', 'email', 'date_joined')
        return Response(users)
