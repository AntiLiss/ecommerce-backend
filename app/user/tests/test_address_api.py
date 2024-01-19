from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_user
from user.serializers import UserSerializer

USER_LIST_URL = reverse("user:user-list")


def get_detail_url(user_id):
    return reverse("user:user-detail", kwargs={"pk": user_id})