import os
import tempfile
from uuid import uuid4
from decimal import Decimal
from PIL import Image
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework import status
from rest_framework.test import APIClient
from .test_models import create_category
from product.models import Product
from product.serializers import ProductSerializer, ProductDetailSerializer

PRODUCT_LIST_URL = reverse("product:product-list")


def get_product_detail_url(product_id):
    """Get url of specific product"""
    return reverse("product:product-detail", kwargs={"pk": product_id})


def get_image_upload_url(product_id):
    """Get url to upload image to specific product"""
    return reverse("product:product-upload-image", args=[product_id])


def create_product(category, **fields):
    default_fields = {
        "name": "testname",
        "description": "some desc",
        "brand": "test brand",
        "price": Decimal("100.99"),
        "stock": 100,
    }
    default_fields.update(**fields)
    return Product.objects.create(category=category, **default_fields)


class PublicProductAPITests(TestCase):
    """Test unauthenticated requests"""

    def setUp(self):
        self.client = APIClient()

    def test_list_products(self):
        """Test listing products"""
        category = create_category()
        create_product(category=category)
        create_product(category=category)
        res = self.client.get(PRODUCT_LIST_URL)
        products = Product.objects.all().order_by("id")
        product_serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, product_serializer.data)

    def test_retrieve_product(self):
        """Test retrieving specific product"""
        category = create_category()
        product = create_product(category=category)
        product_serializer = ProductDetailSerializer(product)
        url = get_product_detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, product_serializer.data)

    def test_no_edit_permission_error(self):
        """Test only admins can create or edit products"""
        payload = {
            "name": "testname",
            "description": "some desc",
            "brand": "test brand",
            "price": Decimal("100.99"),
            "stock": 100,
        }
        res = self.client.post(PRODUCT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        # Make sure the product isn't created
        product_exists = Product.objects.filter(**payload).exists()
        self.assertFalse(product_exists)


class PrivateProductAPITests(TestCase):
    """Test authenticated admin tests"""

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("admin@example.com")
        self.client.force_authenticate(admin)

    def test_create_product(self):
        """Test creating a product"""
        category = create_category()
        payload = {
            "name": "testname",
            "description": "some desc",
            "brand": "test brand",
            "price": Decimal("100.99"),
            "stock": 100,
            "category": category.id,
        }
        res = self.client.post(PRODUCT_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(pk=res.data["id"])
        self.assertEqual(product.category, category)
        payload.pop("category")
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        product_serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, product_serializer.data)

    def test_partial_update_product(self):
        """Test partial update of product"""
        category = create_category()
        original_name = "original-name"
        product = create_product(category=category, name=original_name)

        payload = {
            "description": "new desc",
            "brand": "new brand",
        }
        url = get_product_detail_url(product.id)
        res = self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Make sure original name didn't change
        self.assertEqual(product.name, original_name)
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        product_serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, product_serializer.data)

    def test_full_update_product_error(self):
        """Test full update of product requires all fields"""
        category = create_category()
        product = create_product(category=category)

        payload = {"name": "new name"}
        url = get_product_detail_url(product.id)
        res = self.client.put(url, payload)

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Make sure the product fields didn't change
        for k, v in payload.items():
            self.assertNotEqual(getattr(product, k), v)

    def test_delete_product(self):
        """Test product deletion"""
        category = create_category()
        product = create_product(category=category)
        url = get_product_detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        product_serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, product_serializer.data)

    def test_upload_product_image(self):
        """Test uploading image to existing product"""
        category = create_category()
        product = create_product(category=category)
        url = get_image_upload_url(product.id)

        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(product.image.path))

    def test_upload_product_image_bad_request(self):
        """Test invalid payload"""
        category = create_category()
        product = create_product(category=category)

        url = get_image_upload_url(product.id)
        payload = {"image": "not image"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_product_image(self):
        """Test removing product image"""

        # Create temporary file and save an image in it
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, "JPEG")
            image_file.seek(0)

            # Read created image file and save it in product
            with open(image_file.name, "rb") as file_content:
                category = create_category()
                product = create_product(category=category)
                product.image.save(f"test-name.jpg", File(file_content), save=True)

        url = get_image_upload_url(product.id)
        # Send empty None/null to clear image field
        payload = {"image": None}
        res = self.client.post(url, payload, format="json")

        product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Make sure there is no more image path
        with self.assertRaises(ValueError):
            os.path.exists(product.image.path)

    def test_create_product_with_new_property(self):
        """Test creating product with creating new properties"""
        pass

    def test_create_product_with_existing_property(self):
        """
        Test creating product with already existing properties in db

        It must assign existing property without creating new one
        """
        pass

    def test_create_new_properties_on_update(self):
        """Test create and assign new props when updating product"""
        pass

    def test_assign_existing_props_on_update(self):
        """Test assign already existing props when updating product"""
        pass
