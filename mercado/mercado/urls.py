from django.contrib import admin
from django.urls import path, include
from core.views import home
from market.views import product_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),  # rutas de allauth
    path("", home, name="home"),
     path("productos/", product_list, name="product_list"),
]
