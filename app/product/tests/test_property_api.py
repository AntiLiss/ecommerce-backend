from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_property
from product.models import Property
from product.serializers import PropertySerializer

PROPERTY_LIST_URL = reverse("product:property-list")


def get_property_detail_url(property_id):
    return reverse("product:property-detail", args=[property_id])


class PrivatePropertyTests(TestCase):
    """Test authenticated admin requests"""

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("admin@example.com")
        self.client.force_authenticate(admin)

    def test_no_admin_permission_error(self):
        """Test only admin can make requests"""
        client = APIClient()
        user = get_user_model().objects.create_user("test@example.com")
        client.force_authenticate(user=user)
        res = client.get(PROPERTY_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_props(self):
        """Test listing props"""
        create_property("fabric", "silk")
        create_property("color", "white")
        res = self.client.get(PROPERTY_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        props = Property.objects.all().order_by("id")
        prop_serializer = PropertySerializer(props, many=True)
        self.assertEqual(res.data["results"], prop_serializer.data)

    def test_retrieve_prop(self):
        """Test retrieving specific property"""
        prop = create_property()
        url = get_property_detail_url(prop.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        prop_serializer = PropertySerializer(prop)
        self.assertEqual(res.data, prop_serializer.data)

    def test_create_prop(self):
        """Test creation of property"""
        payload = {"name": "fabric", "value": "cotton"}
        res = self.client.post(PROPERTY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        prop = Property.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(prop, k), v)
        prop_serializer = PropertySerializer(prop)
        self.assertEqual(res.data, prop_serializer.data)

    def test_create_prop_duplication_error(self):
        """Test duplicating prop returns error"""
        payload = {"name": "fabric", "value": "cotton"}
        create_property(**payload)
        res = self.client.post(PROPERTY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure duplicate not created
        prop_count = Property.objects.all().count()
        self.assertEqual(prop_count, 1)

    def test_partial_update_prop(self):
        """Test partial update of property"""
        original_name = "color"
        prop = create_property(name=original_name, value="red")

        payload = {"value": "white"}
        url = get_property_detail_url(prop.id)
        res = self.client.patch(url, payload)

        prop.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(prop.value, payload["value"])
        # Ensure original name didn't change
        self.assertEqual(prop.name, original_name)
        prop_serializer = PropertySerializer(prop)
        self.assertEqual(res.data, prop_serializer.data)

    def test_full_update_prop_error(self):
        """Test PUT update with partial fields returns error"""
        prop = create_property(name="color", value="red")
        payload = {"value": "white"}
        url = get_property_detail_url(prop.id)
        res = self.client.put(url, payload)

        prop.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure fields didn't change
        self.assertNotEqual(prop.value, payload["value"])

    def test_delete_prop(self):
        """Test deleting property"""
        prop = create_property(name="color", value="red")
        url = get_property_detail_url(prop.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
