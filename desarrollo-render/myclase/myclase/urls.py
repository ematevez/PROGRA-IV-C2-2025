from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from core.views import ProductViewSet

#Swagger import
from rest_framework import permissions
from drf_yasg.views import get_schema_view  
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)

schema_view = get_schema_view(
    openapi.Info(  
        title="Mercadito API",
        default_version="v1",
        description="API para manejar productos de Mercadito (compra, venta, trueque, subasta).",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ema@ema.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,    
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),  # allauth
    path("productos/", include("market.urls")),  # users
    path("profiles/", include("perfil.urls")),  # profiles
    path("api/", include(router.urls)),  # API REST
    
    #Sagger URLs endpoints
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
