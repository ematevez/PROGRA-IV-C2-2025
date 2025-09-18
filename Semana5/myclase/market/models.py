from django.conf import settings
from django.db import models

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True, default="Generico")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)  # nuevo campo
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)  # opcional
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # fecha de última modificación

    def __str__(self):
        return self.title

    def is_available(self):
        return self.active and self.stock > 0
