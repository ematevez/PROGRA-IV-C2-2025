from django.db import models

class TelegramMessage(models.Model):
    sender = models.CharField(max_length=50)
    text = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='telegram_photos/', blank=True, null=True)
    audio = models.FileField(upload_to='telegram_audios/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text or 'Media'}"