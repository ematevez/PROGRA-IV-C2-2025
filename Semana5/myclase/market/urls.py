
from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path("list/", views.product_list, name="productlist"),  # market
    path("new/", views.product_create, name="productcreate"),
]



