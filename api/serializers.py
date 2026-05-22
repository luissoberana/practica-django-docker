from rest_framework import serializers

class CalculoImpuestoInputSerializer(serializers.Serializer):
    # Definimos qué datos obligatorios esperamos recibir del cliente en internet
    codigo_iso = serializers.CharField(max_length=2, min_length=2)
    monto = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class CalculoImpuestoOutputSerializer(serializers.Serializer):
    # Definimos qué datos exactos le vamos a responder al cliente
    pais = serializers.CharField()
    porcentaje_aplicado = serializers.FloatField()
    monto_original = serializers.FloatField()
    impuesto_calculado = serializers.FloatField()
    total = serializers.FloatField()