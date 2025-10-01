from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm

def cliente_create(request):
    if request.method == 'POST':   
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            Cliente.objects.create(
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],   
                foto=form.cleaned_data['foto']
                
            )
            messages.success(request, "✅ Cliente agregado correctamente.")
            return redirect("cliente_listar")
        else:
                messages.error(request, "❌ Error al crear cliente. Revisa los datos.")
    else:
        form = ClienteForm()
    return render(request, "cliente_form.html", {"form": form})

def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'cliente_list.html', {'clientes': clientes})

def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    messages.warning(request, "🗑️ Cliente eliminado.")
    return redirect("cliente_listar")