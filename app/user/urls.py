from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRUDView, UserImageAPIView

app_name = "user"

router = DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", UserRUDView.as_view(), name="me"),
    path("me/upload-image/", UserImageAPIView.as_view(), name="upload-image"),
]
