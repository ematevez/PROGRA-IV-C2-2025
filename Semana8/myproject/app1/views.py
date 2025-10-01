from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Producto
from .forms import ProductoForm
from django.urls import reverse_lazy
from django.contrib import messages

class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_form.html'
    success_url = reverse_lazy('app1:producto_listar')
    
    def form_valid(self, form):
        messages.success(self.request, "✅ Producto creado con éxito.")
        return super().form_valid(form)

    
class ProductoListView(ListView):
    model = Producto
    template_name = 'producto_list.html'
    
    
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "producto_form.html"
    success_url = reverse_lazy("app1:producto_listar")

    def form_valid(self, form):
        messages.info(self.request, "✏️ Producto actualizado correctamente.")
        return super().form_valid(form)

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "producto_confirm_delete.html"
    success_url = reverse_lazy("app1:producto_listar")

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "🗑️ Producto eliminado.")
        return super().delete(request, *args, **kwargs)