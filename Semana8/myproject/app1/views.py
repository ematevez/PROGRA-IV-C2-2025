from django.views.generic import CreateView, ListView
from .models import Producto
from .forms import ProductoForm
from django.urls import reverse_lazy


class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_form.html'
    success_url = reverse_lazy('app1:producto_list')
    
    
class ProductoListView(ListView):
    model = Producto
    template_name = 'producto_list.html'
    
    