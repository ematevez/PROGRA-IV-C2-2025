
from django.contrib import admin
from django.urls import path
from market.views import product_list, product_create

urlpatterns = [
    path("lista/", product_list, name="product-list"),  # market
    path("nuevo/", product_create, name="product-create"),
]



