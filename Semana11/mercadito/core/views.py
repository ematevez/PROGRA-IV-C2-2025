from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import CustomUser
from products.models import Product
from presupuestos.models import Presupuesto

class Summary(APIView):
    def get(self, request):
        return Response({
            "usuarios": CustomUser.objects.count(),
            "productos": Product.objects.count(),
            "presupuestos": Presupuesto.objects.count()
        })
