# apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.home.models import UserProfile, Level

class LevelBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'code', 'color']

class UserProfileSerializer(serializers.ModelSerializer):
    reading_level = LevelBriefSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'address', 'date_of_birth',
            'avatar_url', 'native_language',
            'daily_ai_limit', 'reading_level',
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']