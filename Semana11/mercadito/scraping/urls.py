from django.urls import path
from api.views import CompararPrecios, CompararPrecios1
from . import views

urlpatterns = [ 
    path("comparar/<str:nombre>/", CompararPrecios.as_view()), 
    path("comparar1/<str:nombre>/", CompararPrecios1.as_view(), name="comparar-precios1"),
    path('comparara/', views.compare_prices, name='comparara'),

]
