from django.urls import path
from . import views

urlpatterns = [
    path("editar/", views.edit_profile, name="edit_profile"),
    path("ver_perfil/", views.profile_view, name="profile"),
]