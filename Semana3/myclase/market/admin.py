from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "marca", "price", "active", "created_at")  # columnas que ves en la lista
    search_fields = ("title", "description", "marca", "seller__username")          # campos por los que podés buscar
    list_filter = ("active", "created_at", "seller")                       # filtros en la barra lateral
