from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ProductImageSerializer,
    PropertySerializer,
)
from .models import Category, Product, Property


class BaseViewSet(viewsets.ModelViewSet):
    """Basic attributes for viewsets"""

    permission_classes = []
    authentication_classes = [TokenAuthentication]

    # Permis only admins to create and edit
    def get_permissions(self):
        if self.action not in ["list", "retrieve"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CategoryViewSet(BaseViewSet):
    """Manage categories"""

    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")

    # Override deletion to return deleted item in response
    def destroy(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category_serializer = self.get_serializer(category)
        data = category_serializer.data
        category.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)


class ProductViewSet(BaseViewSet):
    """Manage products"""

    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all().order_by("id")

    # Change serializer when "list" and "upload_image" actions
    def get_serializer_class(self):
        if self.action == "list":
            return ProductSerializer
        elif self.action == "upload_image":
            return ProductImageSerializer
        return super().get_serializer_class()

    # Custom action to update specific product's image field
    @action(["post"], detail=True, url_name="upload-image")
    def upload_image(self, request, pk):
        """Upload image to specific product"""
        product = self.get_object()
        image_serializer = self.get_serializer(
            instance=product,
            data=request.data,
        )
        image_serializer.is_valid(raise_exception=True)
        image_serializer.save()
        return Response(image_serializer.data, status.HTTP_200_OK)

    # Override deletion to return deleted item in response
    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product_serializer = self.get_serializer(product)
        data = product_serializer.data
        product.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)


class PropertyViewSet(viewsets.ModelViewSet):
    """Manage product properties"""

    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [TokenAuthentication]
    serializer_class = PropertySerializer
    queryset = Property.objects.all().order_by("id")

    # Override deletion to return deleted item in response
    def destroy(self, request, pk):
        prop = get_object_or_404(Property, pk=pk)
        prop_serializer = self.get_serializer(prop)
        data = prop_serializer.data
        prop.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)
