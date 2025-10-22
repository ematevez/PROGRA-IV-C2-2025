from django.db import models

class Presupuesto(models.Model):
    producto = models.CharField(max_length=200)
    email = models.EmailField()
    mensaje = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Presupuesto para {self.producto} ({self.email})"
