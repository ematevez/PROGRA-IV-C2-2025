from rest_framework.views import APIView
from rest_framework.response import Response
from scraping.utils import comparar_precios, comparar_precios1
from django.shortcuts import render 

class CompararPrecios(APIView):
    def get(self, request, nombre):
        return Response(comparar_precios(nombre))
    
class CompararPrecios1(APIView):
    def get(self, request, nombre):
        return Response(comparar_precios1(nombre))



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