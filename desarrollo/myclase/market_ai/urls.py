from django.urls import path
from . import views

app_name = "market_ai"

urlpatterns = [
    path("price-suggest/", views.price_suggest, name="pricesuggest"),
    path("chat/", views.ai_chat, name="aichat"),
    path("recommend/<int:pk>/", views.recommend_similar, name="recommendsimilar"),
]
