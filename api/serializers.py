from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentRecord, PaymentRecord
from django.conf import settings
from .encryption import encrypt_data, decrypt_data, get_or_create_key

key = get_or_create_key(settings.SECURE_ENCRYPTION_KEY_FILE)


class StudentRecordSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = StudentRecord
        fields = ['id', 'owner', 'full_name', 'course', 'year_level', 'created_at', 'updated_at']


class StudentRecordWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = StudentRecord
        fields = ['id', 'owner', 'full_name', 'course', 'year_level', 'created_at', 'updated_at']


class PaymentRecordSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    card_number = serializers.CharField(write_only=True)
    cvv = serializers.CharField(write_only=True)
    card_number_preview = serializers.SerializerMethodField()

    class Meta:
        model = PaymentRecord
        fields = ['id', 'owner', 'card_holder', 'card_number', 'cvv',
                  'card_number_preview', 'amount', 'created_at']

    def get_card_number_preview(self, obj):
        decrypted = decrypt_data(obj.encrypted_card_number, key)
        return f"****-****-****-{decrypted[-4:]}" if len(decrypted) >= 4 else "****"

    def create(self, validated_data):
        card_number = validated_data.pop('card_number')
        cvv = validated_data.pop('cvv')
        validated_data['encrypted_card_number'] = encrypt_data(card_number, key)
        validated_data['encrypted_cvv'] = encrypt_data(cvv, key)
        return super().create(validated_data)
