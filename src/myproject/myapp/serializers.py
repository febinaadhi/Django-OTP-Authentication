# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}


class TOTPDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTPDevice
        fields = ('id', 'confirmed')

# Add more serializers if needed
