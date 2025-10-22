from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import obtener_precio_coto, comprarar_precios
from django.shortcuts import render
from scraping.utils import comparar_precios1

class CompararPrecios(APIView):
    """
    Devuelve el precio simulado desde Coto + promedio local
    """
    def get(self, request, nombre):
        resultado = obtener_precio_coto(nombre)
        return Response(resultado)



def home(request):
    return render(request, "products/list.html")

def compare_prices(request):
    producto = request.GET.get("producto")
    data = None
    
    if producto:
        # Llama a la función de scraping
        data = comparar_precios1(producto)
    
    return render(request, "products/compare1.html", {
        "data": data, 
        "producto": producto
    })