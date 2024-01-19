from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from user.models import Address, generate_user_image_path


def create_user(email="test@example.com", password=None, **fields):
    return get_user_model().objects.create_user(email, password, **fields)


def create_address(**fields):
    default_fields = {
        "country": "Wakanda",
        "city": "Sample city",
        "street": "Sample street",
        "house": 100,
        "postal_code": "021333",
    }
    default_fields.update(**fields)
    return Address.objects.create(**default_fields)


class UserModelTests(TestCase):
    """Test User model"""

    def test_create_user_with_email(self):
        """Test creating a user with email"""
        email = "test@example.com"
        password = "testpass"
        user = create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_creating_user_without_email_error(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            create_user(email="")

    def test_normalize_new_user_email(self):
        """Test whether new user's email is normalized"""
        sample_emails = [
            ["TEST@EXAMPLE.COM", "TEST@example.com"],
            ["Test@Example.com", "Test@example.com"],
            ["tesT@example.Com", "tesT@example.com"],
        ]

        for raw, expected in sample_emails:
            user = create_user(email=raw)
            self.assertEqual(user.email, expected)

    def test_create_user_with_address(self):
        """Test creating user with address"""
        address = create_address()
        user = create_user(address=address)

        self.assertEqual(user.address, address)

    def test_create_superuser(self):
        """Test creating super user"""
        email = "test@example.com"
        password = "testpass"
        superuser = get_user_model().objects.create_superuser(email, password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_superuser)

    @patch("user.models.uuid4")
    def test_user_image_uuid(self, mock_uuid):
        """Test generating user profile image path"""
        sample_uuid = "sample-uuid"
        mock_uuid.return_value = sample_uuid
        image_path = generate_user_image_path(None, "example.jpg")

        self.assertEqual(image_path, f"uploads/user/{sample_uuid}.jpg")

    def test_create_user_with_address(self):
        """Test creating user with address"""
        address = create_address()
        user = create_user(address=address)

        self.assertEqual(user.address, address)


class AddressModelTests(TestCase):
    """Test address model"""

    def test_create_address(self):
        """Test creating an address"""
        fields = {
            "country": "Wakanda",
            "city": "Sample city",
            "street": "Sample street",
            "house": 100,
            "postal_code": "021333",
        }
        address = create_address(**fields)

        for k, v in fields.items():
            self.assertEqual(getattr(address, k), v)
