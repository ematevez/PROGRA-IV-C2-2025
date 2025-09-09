from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product

def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
    return render(request, "product_list.html", {"products": products})

@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect("product-list")
    else:
        form = ProductForm()
    return render(request, "market/product_form.html", {"form": form})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product-list")
    else:
        form = ProductForm(instance=product)
    return render(request, "market/product_form.html", {"form": form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        product.active = False
        product.save()
        return redirect("product-list")
    return render(request, "market/product_confirm_delete.html", {"product": product})
