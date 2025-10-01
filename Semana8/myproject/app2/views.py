from django.shortcuts import render, redirect
from .models import Cliente
from .forms import ClienteForm

def cliente_create(request):
    if request.method == 'POST':   
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            Cliente.object.create(
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],   
                foto=form.cleaned_data['foto']
                
            )
    else:
        form = ClienteForm()
    return render(request, 'cliente_form.html', {'form': form})

def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'cliente_list.html', {'clientes': clientes})