from django.apps import AppConfig


class PerfilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'perfil'

def ready(self):
    import app.signals
