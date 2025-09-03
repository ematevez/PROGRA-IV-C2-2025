# from django.contrib import admin
# from django.urls import path, include
# from core.views import home


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("", home, name="home"),
#     path("accounts/", include("allauth.urls")),  # allauth
#     path("productos/", include("market.urls")),  # users
# ]
from django.urls import path
from . import views

urlpatterns = [
    path("editar/", views.edit_profile, name="edit_profile"),
    path("ver_perfil/", views.profile_view, name="perfil"),
]
