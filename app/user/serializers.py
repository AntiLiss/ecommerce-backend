from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "name",
            "surname",
            "profile_photo",
            "address",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True, "min_length": 6},
        }

    def create(self, validated_data):
        """Create and return user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
