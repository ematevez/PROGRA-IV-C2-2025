from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required

def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
    return render(request, "product_list.html", {"products": products})

@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect("product-list")
    else:
        form = ProductForm()
    return render(request, "market/product_form.html", {"form": form})