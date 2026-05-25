from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.views import RecaudoPaisView # <-- Asegúrate de importar tu nueva vista
from api.views import CalcularImpuestoAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL de nuestra API real
    path('api/calcular-impuesto/', CalcularImpuestoAPIView.as_view(), name='calcular-impuesto-api'),
    
    # URLs mágicas de Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), # Genera el archivo técnico de la API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Renderiza la web interactiva
    path('recaudo/<int:pais_id>/', RecaudoPaisView.as_view(), name='recaudo-pais'),
]