from rest_framework import serializers
from presupuestos.models import Presupuesto

class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = ["id", "producto", "email", "mensaje", "creado_en"]
