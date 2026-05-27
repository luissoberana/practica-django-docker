from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Pais, HistorialCalculo  # 👈 Cambiado SolicitudImpuesto por HistorialCalculo
from api.views import calcular_impuesto_por_pais

class ValidadorImpuestosAvanzadoTest(TestCase):

    def setUp(self):
        """
        Este método se ejecuta ANTES de cada test.
        Aquí creamos los datos de prueba en la base de datos temporal.
        """
        # Creemos un país de prueba (Colombia con 19%)
        self.pais_co = Pais.objects.create(
            nombre="Colombia",
            codigo_iso="CO",
            porcentaje_impuesto=19.00
        )
        # Creemos un usuario de prueba por si queremos simular una sesión
        self.usuario_test = User.objects.create_user(
            username="juan_dev", 
            password="password123"
        )

    def test_calculo_impuesto_pais_existente(self):
        """Prueba que el cálculo sea exacto para un país que sí existe"""
        # Ejecutamos la función pasando "CO" y un monto de 100
        resultado = calcular_impuesto_por_pais(
            codigo_iso="CO", 
            monto=100, 
            usuario=self.usuario_test
        )

        # Verificaciones del resultado matemático
        self.assertEqual(resultado["pais"], "Colombia")
        self.assertEqual(resultado["porcentaje_aplicado"], 19.00)
        self.assertEqual(resultado["impuesto_calculado"], 19.00)
        self.assertEqual(resultado["total"], 119.00)

        # --- VERIFICACIÓN DEL HISTORIAL (AUDITORÍA) ---
        # 🛡️ Nos aseguramos de contar la tabla correcta (HistorialCalculo)
        self.assertEqual(HistorialCalculo.objects.count(), 1)
        
        # Traemos ese registro de la base de datos para revisar que guardó los datos bien
        historial = HistorialCalculo.objects.first()
        
        # 🌍 Validación inteligente del país (funciona tanto si guardas el Objeto o el Texto directamente)
        if isinstance(historial.pais, str):
            self.assertEqual(historial.pais, "Colombia")
        else:
            self.assertEqual(historial.pais, self.pais_co)
        
        # 💰 Cambiado 'resultado_total' por 'total' para alinearlo con tu base de datos de Neon
        self.assertEqual(float(historial.total), 119.00)

    def test_pais_no_registrado_lanza_error(self):
        """Prueba que si el país no existe, el sistema se proteja y lance un error"""
        with self.assertRaises(ValueError):
            calcular_impuesto_por_pais(codigo_iso="US", monto=100)

    def test_monto_negativo_lanza_error(self):
        """Prueba que los montos negativos sigan estando prohibidos"""
        with self.assertRaises(ValueError):
            calcular_impuesto_por_pais(codigo_iso="CO", monto=-50, usuario=self.usuario_test)