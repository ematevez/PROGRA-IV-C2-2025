from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Si no necesitás campos extra, podés dejarlo vacío
    # Pero agregamos related_name explícito para evitar colisiones
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True
    )

    def __str__(self):
        return self.username
