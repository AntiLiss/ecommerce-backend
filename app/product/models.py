from django.db import models


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
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    # image = models.ImageField()

    def __str__(self):
        return self.name
