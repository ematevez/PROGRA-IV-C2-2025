from django.db import models

class Host(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    mac = models.CharField(max_length=50, blank=True, null=True)
    hostname = models.CharField(max_length=200, blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ip} {self.mac or ''}"