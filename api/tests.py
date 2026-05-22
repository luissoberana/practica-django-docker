from django.test import TestCase
from .views import calcular_impuesto_total # Importamos la función real que acabamos de crear

class ValidadorImpuestosTest(TestCase):
    
    def test_calculo_impuesto_correcto(self):
        """Prueba que el 19% se aplique correctamente a un valor positivo"""
        # Si mandamos 100, el impuesto es 19. El total debería ser 119.
        resultado = calcular_impuesto_total(100)
        
        # Evaluamos que nuestra lógica de negocio dé exactamente 119
        self.assertEqual(resultado, 119)
        
    def test_monto_negativo_lanza_error(self):
        """Prueba que el sistema rechace montos negativos"""
        with self.assertRaises(ValueError):
            calcular_impuesto_total(-50)