"""
URL configuration for mercadito project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from products.views import home, compare_prices, compare_prices1

urlpatterns = [
    path("admin/", admin.site.urls),
    # 👇 Conectás cada app con su subruta API
    path("", home, name="home"),  # 👈 raíz del sitio
    path("comparar/", compare_prices, name="compare-prices"),
    path("comparar1/", compare_prices1, name="compare-prices1"),
    path("api/users/", include("users.api.urls")),
    path("api/products/", include("products.api.urls")),
    path("api/presupuestos/", include("presupuestos.api.urls")),
    path("api/scraping/", include("scraping.api.urls")),
]
