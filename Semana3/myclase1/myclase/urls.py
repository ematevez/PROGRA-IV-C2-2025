from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),  # allauth
    path("productos/", include("market.urls")),  # users
    path("perfil/", include("perfil.urls")),  # perfil
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
