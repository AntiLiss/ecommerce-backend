from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework import viewsets, views
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from .models import Address
from .serializers import UserSerializer, UserImageSerializer, AddressSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Comma separated list of fields to order by: `created_at`",
            ),
        ]
    )
)
class UserListViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Manage User list and retrieve operations"""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all().order_by("id")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]


class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    """Manage User RUD operations"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserImageAPIView(views.APIView):
    """Manage User profile image uploading"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserImageSerializer

    def post(self, request):
        image_serializer = self.serializer_class(
            self.request.user,
            request.data,
        )
        image_serializer.is_valid(raise_exception=True)
        image_serializer.save()
        return Response(data=image_serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Manage addresses"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AddressSerializer

    # Limit address to authenticated user
    def get_queryset(self):
        address = self.request.user.address
        return Address.objects.filter(id=address.id)

    def get_permissions(self):
        # No auth required to create address
        if self.action == "create":
            return []
        return super().get_permissions()
