from django.apps import AppConfig

class MarketAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_ai'

    def ready(self):
        import market_ai.signals  # registra el signal