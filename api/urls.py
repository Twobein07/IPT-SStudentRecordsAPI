from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'student-records', views.StudentRecordViewSet, basename='studentrecord')
router.register(r'payment-records', views.PaymentRecordViewSet, basename='paymentrecord')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
]
