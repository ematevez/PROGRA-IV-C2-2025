from django.shortcuts import render
from market.models import Product
from rest_framework import viewsets , permissions 
from .serializer import ProductSerializer

def home(request):
    products = Product.objects.filter(active=True).order_by("-created_at")[:6]  # últimos 6
    return render(request, "home.html", {"products": products})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
