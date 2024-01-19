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
        read_only_fields = ["id", "profile_photo"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6},
        }

    def create(self, validated_data):
        """Create and return user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user with encrypted password"""
        password = validated_data.pop("password", None)
        super().update(instance, validated_data)
        # Update password separately to hash it
        if password:
            instance.set_password(password)
            instance.save()
        return instance


# Simplified one to return only user id and image in response
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "profile_photo"]
        read_only_fields = ["id"]
        extra_kwargs = {"profile_photo": {"required": True}}