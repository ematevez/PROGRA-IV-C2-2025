from rest_framework import generics
from presupuestos.models import Presupuesto
from .serializers import PresupuestoSerializer
from presupuestos.utils import enviar_a_telegram

class PresupuestoCreate(generics.CreateAPIView):
    queryset = Presupuesto.objects.all()
    serializer_class = PresupuestoSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        mensaje = (
            f"📩 Nuevo presupuesto recibido\n\n"
            f"Producto: {instance.producto}\n"
            f"Email: {instance.email}\n"
            f"Mensaje: {instance.mensaje}"
        )
        enviar_a_telegram(mensaje)
