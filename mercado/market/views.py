from django.shortcuts import render
from .models import Product

def product_list(request):
    qs = Product.objects.filter(active=True).order_by("-created_at")
    return render(request, "market/product_list.html", {"products": qs})
