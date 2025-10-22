from django.urls import path
from .views import CompararPrecios, CompararPrecios1, compare_prices

urlpatterns = [
    path("comparar/<str:nombre>/", CompararPrecios.as_view(), name="comparar-precios"),
    path("comparar1/<str:nombre>/", CompararPrecios1.as_view(), name="comparar-precios1"),
    path('comparara/', compare_prices, name='comparara'),
]
