from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'phone_number', 'email', 'password']
        extra_kwargs = {
            'name': {'required': True, 'help_text': 'Full name of the user'},
            'phone_number': {'required': True, 'help_text': 'Unique phone number to use as username'},
            'email': {'required': False, 'help_text': 'Optional email address'},
            'password': {'write_only': True, 'help_text': 'Password for the user account'},
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password']

class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['token']