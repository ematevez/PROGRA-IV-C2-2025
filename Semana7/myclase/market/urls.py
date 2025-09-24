from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path("", views.product_list, name="productlist"),
    path("create/", views.product_create, name="productcreate"),
    path("edit/<int:pk>/", views.product_edit, name="product-edit"),
    path("delete/<int:pk>/", views.product_delete, name="product-delete"),
    path("cart/", views.view_cart, name="view-cart"),
    path("add/<int:product_id>/", views.add_to_cart, name="add-to-cart"),

    # Mercado Pago
    # path("pago/<int:product_id>/", views.create_preference, name="crear-preferencia"),
    path("pago-carrito/", views.create_preference_cart, name="crear-preferencia-carrito"),
]
