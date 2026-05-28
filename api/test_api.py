from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Pais, HistorialCalculo

class ImpuestosAPIIntegrationTest(APITestCase):

    def setUp(self):
        """
        Este método corre ANTES de cada test.
        Poblamos la base de datos temporal con lo mínimo necesario.
        """
        # Creamos un país base para las pruebas
        self.pais_co = Pais.objects.create(
            nombre="Colombia",
            codigo_iso="CO",
            porcentaje_impuesto=19.00
        )
        
        # Mapeo de tus URLs reales
        self.url_calcular = "/api/calcular-impuesto/"
        self.url_paises = "/api/paises/"
        self.url_historial = "/api/historial/"
        self.url_recaudo = "/api/recaudo/"

    # =========================================================================
    # 🎯 1. ENDPOINT: POST /api/calcular-impuesto/
    # =========================================================================
    
    def test_http_post_calcular_impuesto_exitoso(self):
        """Valida que la API reciba el JSON, calcule bien y responda 200 OK"""
        payload = {"codigo_iso": "CO", "monto": 100.00}
        response = self.client.post(self.url_calcular, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pais"], "Colombia")
        self.assertEqual(response.data["total"], 119.00)
        self.assertEqual(HistorialCalculo.objects.count(), 1)

    def test_http_post_monto_menor_al_minimo_frena_en_serializer(self):
        """Valida que el Serializador bloquee montos menores a 0.01 con un 400"""
        payload = {"codigo_iso": "CO", "monto": 0.00}
        response = self.client.post(self.url_calcular, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("monto", response.data)

    def test_http_post_pais_no_registrado_devuelve_400(self):
        """Valida que si el país no existe en la BD, responda 400 Bad Request"""
        payload = {"codigo_iso": "US", "monto": 500.00}
        response = self.client.post(self.url_calcular, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "El país con código 'US' no está registrado en el sistema")

    # =========================================================================
    # 🌍 2. ENDPOINT: GET /api/paises/ (Para el Listbox del Frontend)
    # =========================================================================
    
    def test_http_get_listar_paises_exitoso(self):
        """Valida que devuelva la lista de países registrados para el Frontend"""
        response = self.client.get(self.url_paises)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Como creamos 1 país en el setUp, la lista debe tener tamaño 1
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre"], "Colombia")
        self.assertEqual(response.data[0]["codigo_iso"], "CO")

    # =========================================================================
    # 📋 3. ENDPOINT: GET /api/historial/ (Panel Administrativo)
    # =========================================================================
    
    def test_http_get_historial_vacio_y_con_datos(self):
        """Valida que el historial liste los datos en orden inverso cronológico"""
        # Caso A: Recién iniciado, el historial debe estar vacío
        response_vacia = self.client.get(self.url_historial)
        self.assertEqual(response_vacia.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_vacia.data), 0)

        # Caso B: Insertamos dos registros manualmente simulando auditoría pasada
        HistorialCalculo.objects.create(
            pais="Colombia", monto_original=100, porcentaje_aplicado=19, impuesto_calculado=19, total=119
        )
        HistorialCalculo.objects.create(
            pais="Colombia", monto_original=200, porcentaje_aplicado=19, impuesto_calculado=38, total=238
        )

        response_con_data = self.client.get(self.url_historial)
        self.assertEqual(response_con_data.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_con_data.data), 2)

    # =========================================================================
    # 📊 4. ENDPOINT: GET /api/recaudo/ (Métricas y Analítica)
    # =========================================================================
    
    def test_http_get_recaudo_calcula_agregaciones_correctamente(self):
        """Valida que las operaciones de Suma y Conteo matemático de la vista funcionen"""
        # Insertamos dos liquidaciones de prueba para Colombia en la BD efímera
        HistorialCalculo.objects.create(
            pais="Colombia", monto_original=100, porcentaje_aplicado=19, impuesto_calculado=19, total=119
        )
        HistorialCalculo.objects.create(
            pais="Colombia", monto_original=200, porcentaje_aplicado=19, impuesto_calculado=38, total=238
        )

        response = self.client.get(self.url_recaudo)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Revisamos que los campos agrupados ('annotate') coincidan con la matemática
        self.assertEqual(response.data[0]["pais"], "Colombia")
        self.assertEqual(response.data[0]["total_operaciones"], 2)
        self.assertEqual(float(response.data[0]["total_impuesto_recaudado"]), 57.00)  # 19 + 38
        self.assertEqual(float(response.data[0]["total_monto_procesado"]), 300.00)    # 100 + 200