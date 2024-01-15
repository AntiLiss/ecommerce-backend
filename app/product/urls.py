from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, PropertyViewSet

app_name = "product"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("properties", PropertyViewSet, basename="property")

urlpatterns = router.urls
