from django.urls import path
from .views import PresupuestoCreate

urlpatterns = [ path("create/", PresupuestoCreate.as_view(), name="presupuesto-create") ]
