from django.urls import path
from .views import MensajeListCreate

urlpatterns = [ path("messages/", MensajeListCreate.as_view()), ]
