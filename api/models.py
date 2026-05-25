from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuarios de Django

class Pais(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    codigo_iso = models.CharField(max_length=2, unique=True)
    porcentaje_impuesto = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje_impuesto}%)" # Define como se va a mostrar el país 
    # en el panel de control de Django Admin


# --- NUEVA TABLA: HISTORIAL DE SOLICITUDES ---
class SolicitudImpuesto(models.Model):
    # ¿Quién? 
    # Vinculamos la solicitud con el usuario que la hizo. 
    # 'on_delete=models.SET_NULL' significa que si borramos al usuario, el historial no se borra (queda como Anónimo).
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ¿De qué país se consultó?
    # Vinculamos esta fila con la tabla Pais que creamos arriba.
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    
    # ¿Cuándo?
    # 'auto_now_add=True' le dice a Django: "Graba la fecha y hora exacta del servidor automáticamente cuando se cree este registro".
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Los datos del cálculo
    monto_original = models.DecimalField(max_digits=12, decimal_places=2)
    impuesto_calculado = models.DecimalField(max_digits=12, decimal_places=2)
    resultado_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        # Un resumen amigable para el panel de control
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"Cálculo {self.pais.codigo_iso} por {usuario_str} el {self.fecha_creacion.strftime('%d/%m/%Y')}"

class Moneda(models.Model):
    nombre = models.CharField(max_length=50) # Ej: "Peso Colombiano"
    simbolo = models.CharField(max_length=5)  # Ej: "$"