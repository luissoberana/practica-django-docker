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
