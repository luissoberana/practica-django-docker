from decimal import Decimal
from api.models import Pais, SolicitudImpuesto

def calcular_impuesto_por_pais(codigo_iso, monto, usuario=None):
    """
    Busca el país por su código ISO en la base de datos, calcula el impuesto
    correspondiente y registra la consulta en la tabla de historial.
    """
    # 1. Asegurarnos de que el monto no sea negativo
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")

    try:
        # 2. Ir a Neon.tech a buscar el país usando el ORM de Django
        # Convertimos el código a mayúsculas por si acaso (ej: "co" -> "CO")
        pais = Pais.objects.get(codigo_iso=codigo_iso.upper())
    except Pais.DoesNotExist:
        # Si el usuario digita un país que no tenemos (ej: "US"), lanzamos un error claro
        raise ValueError(f"El país con código '{codigo_iso}' no está registrado en el sistema")

    # 3. Convertir el monto a Decimal para hacer matemática financiera exacta (evita errores de redondeo de Python)
    monto_decimal = Decimal(str(monto))
    
    # 4. Hacer el cálculo usando el porcentaje real que extrajimos de la base de datos
    # Ejemplo: Si el impuesto es 19.00%, multiplicamos por (19.00 / 100)
    porcentaje = pais.porcentaje_impuesto / Decimal('100')
    impuesto_calculado = monto_decimal * porcentaje
    resultado_total = monto_decimal + impuesto_calculado

    # 5. --- ¡NUEVA FUNCIÓN DE HISTORIAL! ---
    # Guardamos un registro físico en la tabla de auditoría antes de terminar
    SolicitudImpuesto.objects.create(
        usuario=usuario, # Puede ser un usuario real o None (Anónimo)
        pais=pais,
        monto_original=monto_decimal,
        impuesto_calculado=impuesto_calculado,
        resultado_total=resultado_total
    )

    # 6. Devolvemos los datos listos
    return {
        "pais": pais.nombre,
        "porcentaje_aplicado": float(pais.porcentaje_impuesto),
        "monto_original": float(monto_decimal),  # 
        "impuesto_calculado": float(impuesto_calculado),
        "total": float(resultado_total)
    }

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.db import connection 
from .serializers import CalculoImpuestoInputSerializer, CalculoImpuestoOutputSerializer

class CalcularImpuestoAPIView(APIView):
    
    # Este decorador le enseña a Swagger qué datos requiere esta API y qué va a responder
    @extend_schema(
        request=CalculoImpuestoInputSerializer,
        responses={200: CalculoImpuestoOutputSerializer},
        summary="Calcula el impuesto según el país y registra en el historial"
    )
    def post(self, request):
        # 1. Validamos los datos que nos enviaron por internet usando el serializador
        serializer = CalculoImpuestoInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Si son válidos, extraemos las variables limpias
        codigo_iso = serializer.validated_data['codigo_iso']
        monto = serializer.validated_data['monto']
        
        try:
            # 3. Reutilizamos tu lógica potente que va a Neon y guarda el historial
            # Pasamos request.user si el usuario está autenticado en el panel, de lo contrario será None (Anónimo)
            usuario = request.user if request.user.is_authenticated else None
            resultado = calcular_impuesto_por_pais(codigo_iso, monto, usuario=usuario)
            
            # 4. Devolvemos la respuesta exitosa
            return Response(resultado, status=status.HTTP_200_OK)
            
        except ValueError as e:
            # Si nuestra lógica arrojó un error (ej: el país no existe), respondemos un error limpio
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RecaudoPaisView(APIView):
    """
    Vista que consume el Stored Procedure 'calcular_total_recaudado'
    para obtener la suma total de impuestos por país directamente desde Neon.
    """
    def get(self, request, pais_id):
        # 1. Abrimos un "túnel" directo a la base de datos
        with connection.cursor() as cursor:
            # 2. Ejecutamos el Stored Procedure pasándole el ID del país de forma segura
            cursor.execute("SELECT calcular_total_recaudado(%s);", [pais_id])
            
            # 3. Atrapamos el resultado que escupe Neon
            resultado = cursor.fetchone()
            
            # 4. Limpiamos el dato (si no hay nada, devolvemos 0.00)
            total = resultado[0] if resultado else 0.00
            
        # 5. Devolvemos el JSON bonito para el cliente
        return Response({
            "pais_id": pais_id,
            "total_recaudado": total
        })