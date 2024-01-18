from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, PropertyViewSet, ReviewViewSet

app_name = "product"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("properties", PropertyViewSet, basename="property")
router.register("reviews", ReviewViewSet)

urlpatterns = router.urls
