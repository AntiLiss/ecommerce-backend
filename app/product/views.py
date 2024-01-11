from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .serializers import CategorySerializer
from .models import Category


class CategoryViewSet(viewsets.ModelViewSet):
    """Manage categories"""

    permission_classes = []
    authentication_classes = [TokenAuthentication]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    # Order categories by id
    def get_queryset(self):
        return self.queryset.order_by("id")

    # Permis only admins to create and edit categories
    def get_permissions(self):
        if self.action not in ["list", "retrieve"]:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()

    # Override deletion to return deleted item in response
    def destroy(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category_serializer = CategorySerializer(category)
        data = category_serializer.data
        category.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)
