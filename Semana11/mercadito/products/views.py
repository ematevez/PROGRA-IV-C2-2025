from django.shortcuts import render
from scraping.utils import comparar_precios, comparar_precios1

def home(request):
    return render(request, "products/list.html")

def compare_prices(request):
    producto = request.GET.get("producto")
    data = None
    if producto:
        data = comparar_precios(producto)
    return render(request, "products/compare.html", {"data": data, "producto": producto})

def compare_prices1(request):
    producto = request.GET.get("producto")
    data = None
    if producto:
        data = comparar_precios1(producto)
    return render(request, "products/compare1.html", {"data": data, "producto": producto})