from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers  # ◄-- CORREGIDO: Importación real de DRF
from drf_spectacular.utils import extend_schema
from django.db import connection 
from api.models import Pais, HistorialCalculo  # ◄-- CORREGIDO: Usamos la tabla del historial de forma consistente
from .serializers import CalculoImpuestoInputSerializer, CalculoImpuestoOutputSerializer
from django.db.models import Sum, Count

def calcular_impuesto_por_pais(codigo_iso, monto, usuario=None):
    """
    Busca el país por su código ISO en la base de datos, calcula el impuesto
    corresponding y registra la consulta en la tabla de historial de Neon.
    """
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")

    try:
        pais = Pais.objects.get(codigo_iso=codigo_iso.upper())
    except Pais.DoesNotExist:
        raise ValueError(f"El país con código '{codigo_iso}' no está registrado en el sistema")

    monto_decimal = Decimal(str(monto))
    porcentaje = pais.porcentaje_impuesto / Decimal('100')
    impuesto_calculado = monto_decimal * porcentaje
    resultado_total = monto_decimal + impuesto_calculado

    # 🎯 CORREGIDO: Ahora sí guardamos en la misma tabla que lee el Frontend
    HistorialCalculo.objects.create(
        pais=pais.nombre,
        monto_original=monto_decimal,
        porcentaje_aplicado=pais.porcentaje_impuesto,
        impuesto_calculado=impuesto_calculado,
        total=resultado_total
    )

    return {
        "pais": pais.nombre,
        "porcentaje_aplicado": float(pais.porcentaje_impuesto),
        "monto_original": float(monto_decimal),  
        "impuesto_calculado": float(impuesto_calculado),
        "total": float(resultado_total)
    }

# ==========================================
# 📋 SERIALIZADORES
# ==========================================

class HistorialCalculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialCalculo
        fields = ['id', 'pais', 'monto_original', 'porcentaje_aplicado', 'impuesto_calculado', 'total', 'fecha_creacion']

# ==========================================
# 🎛️ VISTAS DE LA API (API VIEWS)
# ==========================================

class CalcularImpuestoAPIView(APIView):
    @extend_schema(
        request=CalculoImpuestoInputSerializer,
        responses={200: CalculoImpuestoOutputSerializer},
        summary="Calcula el impuesto según el país y registra en el historial"
    )
    def post(self, request):
        serializer = CalculoImpuestoInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        codigo_iso = serializer.validated_data['codigo_iso']
        monto = serializer.validated_data['monto']
        
        try:
            resultado = calcular_impuesto_por_pais(codigo_iso, monto, usuario=None)
            return Response(resultado, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListarPaisesAPIView(APIView):
    """
    Endpoint dinámico que devuelve todos los países registrados 
    en Neon para alimentar el Listbox del Frontend.
    """
    def get(self, request):
        paises = Pais.objects.values('id', 'nombre', 'codigo_iso', 'porcentaje_impuesto')
        return Response(paises, status=status.HTTP_200_OK)


class HistorialCalculoAPIView(APIView):
    @extend_schema(
        responses={200: HistorialCalculoSerializer(many=True)},
        summary="Obtiene todo el historial de liquidaciones para el panel administrativo"
    )
    def get(self, request):
        registros = HistorialCalculo.objects.all().order_by('-fecha_creacion')
        serializer = HistorialCalculoSerializer(registros, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RecaudoPaisAPIView(APIView):
    @extend_schema(
        summary="Obtiene el acumulado total de recaudo e impuestos por cada país"
    )
    def get(self, request):
        """
        Agrupa todo el historial por país y calcula la suma total de impuestos,
        montos originales y cantidad de operaciones realizadas.
        """
        resumen = HistorialCalculo.objects.values('pais').annotate(
            total_impuesto_recaudado=Sum('impuesto_calculado'),
            total_monto_procesado=Sum('monto_original'),
            total_operaciones=Count('id')
        ).order_by('-total_impuesto_recaudado') # Ordena de mayor a menor recaudo
        
        return Response(resumen, status=status.HTTP_200_OK)