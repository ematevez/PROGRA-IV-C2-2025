from django.urls import path
from .views import ProductoCreateView, ProductoListView

urlpatterns = [
    path("nuevo/", ProductoCreateView.as_view(), name="producto_crear"),
    path("lista/", ProductoListView.as_view(), name="producto_listar"),
]
