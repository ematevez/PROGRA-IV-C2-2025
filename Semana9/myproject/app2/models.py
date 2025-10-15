from django.db import models

class Cliente (models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    foto = models.ImageField(upload_to='clientes/')
    
    def __str__(self):
        return self.nombre
    
