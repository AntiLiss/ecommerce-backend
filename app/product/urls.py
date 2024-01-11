from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

app_name = "product"

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
