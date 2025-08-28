# core/serializers.py
from rest_framework import serializers
from .models import User, Session
from django.contrib.auth import authenticate
import uuid
from datetime import datetime, timedelta


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        print("Creating user with data:", validated_data)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        print("User created:", user.email)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        print("Validating login for email:", email)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            print("User found:", user.username)
        except User.DoesNotExist:
            print("User not found for email:", email)
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials: User not found"]})

        # Authenticate using email and password
        user = authenticate(email=email, password=password)
        if not user:
            print("Authentication failed for email:", email)
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials: Incorrect password"]})

        print("Authentication successful for user:", user.username)
        data['user'] = user
        return data


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['token', 'expires_at']
