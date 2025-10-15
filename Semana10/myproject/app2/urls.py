from django.urls import path
from . import views

urlpatterns = [
   path('nuevo/', views.cliente_create, name='cliente_crear'),
   path('lista/', views.cliente_list, name='cliente_listar'),
]
