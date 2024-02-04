from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_user, create_address
from user.models import Address
from user.serializers import AddressSerializer


ADDRESS_LIST_URL = reverse("user:address-list")


def get_detail_url(address_id):
    return reverse("user:address-detail", kwargs={"pk": address_id})


class PublicAddressAPITests(TestCase):
    """Test unauthenticated requests"""

    def test_create_address(self):
        """Test creating address"""
        payload = {
            "country": "Wakanda",
            "city": "Sample city",
            "street": "Sample street",
            "house": 100,
            "postal_code": "021333",
        }
        res = self.client.post(ADDRESS_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        address = Address.objects.get(id=res.data["id"])
        serializer = AddressSerializer(address)
        self.assertEqual(serializer.data, res.data)


class PrivateAddressAPITests(TestCase):
    """Test authenticated requests"""

    def setUp(self):
        self.address = create_address(street="Groove St")
        self.user = create_user(address=self.address)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_own_address(self):
        """Test retrieving address of user himself"""
        url = get_detail_url(self.address.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = AddressSerializer(self.address)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_address(self):
        """Test partially updating address"""
        payload = {"country": "new country"}
        url = get_detail_url(self.address.id)
        res = self.client.patch(url, payload)
        serializer = AddressSerializer(self.address)

        self.address.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(self.address.country, payload["country"])
        # Ensure original field didn't change
        self.assertEqual(self.address.street, "Groove St")

    def test_full_update_address(self):
        """Test full update or address requires all fields"""
        payload = {"country": "new country"}
        url = get_detail_url(self.address.id)
        res = self.client.put(url, payload)

        self.address.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure the address didn't change
        self.assertNotEqual(self.address.country, payload["country"])

    def test_delete_address(self):
        """Test address deletion"""
        url = get_detail_url(self.address.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
