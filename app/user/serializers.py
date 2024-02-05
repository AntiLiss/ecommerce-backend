from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Address
from .tests.test_models import create_user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["country", "city", "street", "house", "postal_code"]
        read_only_fields = ["id"]
        required_fields = ["country, street"]


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = get_user_model()
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
        address_data = validated_data.pop("address", None)
        # Create user with hashing password
        user = get_user_model().objects.create_user(**validated_data)
        # Create address and relate it to user
        self._set_address(address_data, user)
        return user

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        password = validated_data.pop("password", None)
        super().update(instance, validated_data)
        # Update password separately to hash it
        if password:
            instance.set_password(password)

        # Reset address
        if address_data is not None:
            if instance.address:
                instance.address.delete()
            if address_data == {}:
                instance.address = None
            elif address_data:
                self._reset_address(address_data, instance)

        instance.save()
        return instance

    def _set_address(self, address_data, user):
        """Create address and relate it to user"""
        if not address_data:
            return
        address_obj = Address.objects.create(**address_data)
        user.address = address_obj
        user.save()

    # Raises error if not all address fields provided when updating
    def _reset_address(self, address_data, user):
        """Reset address with ensuring no missing fields"""
        missing_fields = set(AddressSerializer.Meta.fields) - set(address_data)
        if missing_fields:
            msg = f"These fields are required: {missing_fields}"
            raise serializers.ValidationError(msg)
        self._set_address(address_data, user)


# Simplified one to return only user id and image in response
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "profile_photo"]
        read_only_fields = ["id"]
        extra_kwargs = {"profile_photo": {"required": True}}
