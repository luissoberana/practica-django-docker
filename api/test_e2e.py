import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright

class ImpuestosE2ETest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_interaccion_formulario_swagger(self):
        """Playwright abre el navegador, llena el formulario de Swagger y ejecuta el endpoint"""
        page = self.browser.new_page()
        
        # Creamos la carpeta de capturas desde el inicio
        folder_capturas = "screenshots"
        os.makedirs(folder_capturas, exist_ok=True)
        
        try:
            page.goto(f"{self.live_server_url}/api/docs/")
            
            # 1. Desplegamos el endpoint POST
            endpoint_post = page.locator(".opblock-post")
            endpoint_post.click()
            
            # 2. Clic en "Try it out"
            btn_try_it_out = page.locator("button.try-out__btn")
            btn_try_it_out.click()
            
            # 3. Llenamos el JSON limpia y directamente
            json_textarea = page.locator("textarea.body-param__text")
            json_textarea.clear()
            payload_prueba = '{\n  "codigo_iso": "CO",\n  "monto": 100.00\n}'
            json_textarea.fill(payload_prueba)
            
            # 4. Ejecutamos la petición HTTP real
            btn_execute = page.locator("button.execute")
            btn_execute.click()
            
            # 5. 🎯 OPTIMIZACIÓN: Buscamos el bloque de respuestas de forma más global
            # Aumentamos el tiempo a 15 segundos (15000ms) por si Neon está frío
            bloque_respuesta = page.locator(".responses-wrapper")
            bloque_respuesta.wait_for(state="visible", timeout=15000)
            
            # 📸 CAPTURA DE ÉXITO: Si llegó hasta aquí, tomamos la foto del resultado
            page.screenshot(path=f"{folder_capturas}/screenshot_endpoint_ejecutado.png")
            
            # Validamos que la pantalla contenga la confirmación del éxito
            self.assertTrue(page.locator("text=200").is_visible() or page.locator("text=Success").is_visible())

        except Exception as e:
            # 📸 CAPTURA DE ERROR: Si algo falla, el robot nos deja la evidencia de qué estaba viendo
            page.screenshot(path=f"{folder_capturas}/screenshot_error.png")
            raise e
        finally:
            page.close()