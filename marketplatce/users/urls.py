from django.urls import path
from .views import user_form
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls + [
    path("form/", user_form, name="user_form"),
]
