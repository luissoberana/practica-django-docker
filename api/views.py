from django.shortcuts import render

# --- ESTA ES NUESTRA LÓGICA DE NEGOCIO ---
def calcular_impuesto_total(monto):
    """
    Recibe un monto, le aplica un 19% de impuesto (IVA) 
    y retorna el total a pagar.
    """
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")
    
    impuesto = monto * 0.19
    return monto + impuesto