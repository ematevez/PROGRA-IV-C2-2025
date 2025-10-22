from django.db import models
from django.conf import settings
from products.models import Product

class Comentario(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
