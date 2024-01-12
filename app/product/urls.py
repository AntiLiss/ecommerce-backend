from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

app_name = "product"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)

urlpatterns = router.urls
