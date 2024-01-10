import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def generate_user_image_path(instance, filename):
    """Generate user image path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "user", filename)


class Address(models.Model):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house = models.IntegerField()
    postal_code = models.CharField(max_length=12)


class UserManager(BaseUserManager):
    """User model manager"""

    def create_user(self, email, password=None, **fields):
        """Create and return user"""
        if not email:
            raise ValueError("User must have an email!")

        user = self.model(
            email=self.normalize_email(email),
            **fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **fields):
        if not email:
            raise ValueError("User must have an email!")

        superuser = self.model(
            email=self.normalize_email(email),
            **fields,
        )
        superuser.set_password(password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """User (admin/customer) model"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100, blank=True)
    surname = models.CharField(max_length=100, blank=True)
    is_staff = models.BooleanField(default=False)
    profile_photo = models.ImageField(
        upload_to=generate_user_image_path, blank=True, null=True
    )
    address = models.OneToOneField(
        to=Address,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return self.email
