from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    # path('webhook/', views.telegram_webhook, name='telegram_webhook'),
]
