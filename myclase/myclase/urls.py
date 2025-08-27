from django.contrib import admin
from django.urls import path, include
from core.views import home


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),  # allauth
    path("productos/", include("market.urls")),  # users
]
