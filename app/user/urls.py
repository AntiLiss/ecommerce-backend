from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserListViewSet, ProfileRUDView, ProfileImageAPIView

app_name = "user"

router = DefaultRouter()
router.register("users", UserListViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", ProfileRUDView.as_view(), name="me"),
    path("me/upload-image/", ProfileImageAPIView.as_view(), name="upload-image"),
]
