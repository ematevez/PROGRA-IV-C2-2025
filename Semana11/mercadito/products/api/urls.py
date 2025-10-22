from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r"", ProductViewSet)  # /api/products/

urlpatterns = router.urls
