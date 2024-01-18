import os
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model


def generate_product_image_path(instance, filename):
    """Generate product image path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "product", filename)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # Ensure name is unique in case-insensitive manner before saving
    def save(self, *args, **kwargs):
        if Category.objects.filter(
            name__iexact=self.name,
        ):
            msg = f"Category with this Name ({self.name}) already exists!"
            raise ValueError(msg)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Property(models.Model):
    """Product property model"""

    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    # Ensure combination of fields are unique in case-insensitive
    # manner before saving
    def save(self, *args, **kwargs):
        if Property.objects.filter(
            name__iexact=self.name,
            value__iexact=self.value,
        ):
            msg = f"Property with this Name ({self.name}) and Value ({self.value}) already exists!"
            raise ValueError(msg)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(
        upload_to=generate_product_image_path,
        blank=True,
        null=True,
    )
    rating = models.FloatField(
        blank=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    properties = models.ManyToManyField(
        to=Property,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    commentary = models.TextField(blank=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Ensure user can leave only 1 review for the product
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_review"
            )
        ]
