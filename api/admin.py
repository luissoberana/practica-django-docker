from django.contrib import admin
from .models import Pais, SolicitudImpuesto

# Configuración elegante para la tabla de Países
@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista principal
    list_display = ('nombre', 'codigo_iso', 'porcentaje_impuesto')
    # Buscador integrado por nombre o código
    search_fields = ('nombre', 'codigo_iso')


# Configuración elegante para la tabla de Historial
@admin.register(SolicitudImpuesto)
class SolicitudImpuestoAdmin(admin.ModelAdmin):
    # Columnas para la auditoría (Quién, Cuándo, Cuánto)
    list_display = ('id', 'usuario', 'pais', 'monto_original', 'impuesto_calculado', 'resultado_total', 'fecha_creacion')
    # Filtro lateral automático por país o fecha
    list_filter = ('pais', 'fecha_creacion')
    # Hacer que todo el historial sea de "Solo Lectura" (un administrador no debería alterar el historial)
    readonly_fields = ('usuario', 'pais', 'monto_original', 'impuesto_calculado', 'resultado_total', 'fecha_creacion')

from .models import Moneda # O el nombre de tu nuevo modelo
admin.site.register(Moneda)