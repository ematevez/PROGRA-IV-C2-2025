from rest_framework import generics
from .models import Mensaje
from .serializers import MensajeSerializer

class MensajeListCreate(generics.ListCreateAPIView):
    queryset = Mensaje.objects.all().order_by("-creado_en")[:50]
    serializer_class = MensajeSerializer
