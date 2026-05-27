from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# 🎯 CORREGIDO: Eliminamos la línea de RecaudoPaisView que causaba el crash
from api.views import CalcularImpuestoAPIView, ListarPaisesAPIView, HistorialCalculoAPIView, RecaudoPaisAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL de nuestra API real
    path('api/calcular-impuesto/', CalcularImpuestoAPIView.as_view(), name='calcular-impuesto-api'),
    path('api/paises/', ListarPaisesAPIView.as_view(), name='listar-paises'),
    path('api/historial/', HistorialCalculoAPIView.as_view(), name='historial'),
    path('api/recaudo/', RecaudoPaisAPIView.as_view(), name='recaudo-paises'),
    
    # URLs mágicas de Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), 
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),    
]