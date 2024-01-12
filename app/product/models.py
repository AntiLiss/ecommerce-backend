import os
from uuid import uuid4
from django.db import models


def generate_product_image_path(instance, filename):
    """Generate product image path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "product", filename)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)  # TODO make min=1
    stock = models.IntegerField()  # TODO make min=0
    image = models.ImageField(
        upload_to=generate_product_image_path,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    # properties = models.ManyToManyField()

    def __str__(self):
        return self.name
