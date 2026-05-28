# 🧮 Engine de Validación e Impuestos API (Backend Búnker)

Este repositorio contiene el núcleo lógico de cálculo, estandarización y auditoría fiscal para transacciones en Latinoamérica. La plataforma está diseñada bajo una arquitectura contenerizada de alta disponibilidad, pensada específicamente para ser consumida de manera automatizada y masiva por plataformas de integración como **n8n**, asegurando registros inmutables de auditoría en microsegundos.

---

## 📋 Tabla de Contenidos
1. [Descripción General y Arquitectura](#-descripción-general-y-arquitectura)
2. [Estructura de Carpetas del Proyecto](#-estructura-de-carpetas-del-proyecto)
3. [Configuración del Entorno Virtual (`.env`)](#-configuración-del-entorno-virtual-env)
4. [Instalación Paso a Paso (Entorno Local)](#-instalación-paso-a-paso-entorno-local)
5. [Población Inicial de Datos (Seed/Fixtures)](#-población-inicial-de-datos-seedfixtures)
6. [Estrategia de Calidad: Búnker de Testing (10/10)](#-estrategia-de-calidad-búnker-de-testing-1010)
7. [Documentación Extendida de Endpoints (JSON Payloads)](#-documentación-extendida-de-endpoints-json-payloads)
8. [Guía de Despliegue en Producción](#-guía-de-despliegue-en-producción)
9. [Solución de Problemas Frecuentes (Troubleshooting)](#-solución-de-problemas-frecuentes-troubleshooting)

---

## 🎯 Descripción General y Arquitectura

El sistema centraliza las tasas impositivas dinámicas de la región eliminando la lógica fiscal de las aplicaciones cliente o de los flujos de n8n. 

### 🔄 Flujo de Datos del Sistema:
1. **Petición Cliente:** Un webhook de n8n o un cliente externo envía un JSON con el monto y el código ISO del país (ej: `CO`).
2. **Capa de Serialización:** Django REST Framework valida los tipos de datos y previene inyecciones o payloads malformados.
3. **Capa de Negocio:** El sistema consulta la tasa impositiva en la base de datos relacional y realiza cálculos de precisión matemática financiera (`Decimal`).
4. **Persistencia Mutante:** Se genera de forma asíncrona un registro histórico único e inmutable para auditorías de rendimiento.
5. **Respuesta:** Se devuelve un JSON estandarizado con código HTTP `200 OK`.

Todo el ecosistema corre sobre una base idéntica en Linux (**Debian Bookworm**), lo que mitiga cualquier discrepancia entre entornos de desarrollo, staging y producción.

---

## 📁 Estructura de Carpetas del Proyecto

```text
validador-backend/
├── .github/workflows/
│   └── ci.yml             # Workflow de GitHub Actions (Estrategia de caché + Tríada de Tests)
├── api/
│   ├── migrations/        # Historial de versiones del esquema de base de datos de Django
│   ├── models.py          # Modelos ORM: Pais (Configuración) e HistorialCalculo (Auditoría)
│   ├── serializers.py     # Esquemas de validación de entrada y formateo de salida de JSON
│   ├── test_api.py        # Capa 2: Tests de integración de Endpoints e inyección HTTP
│   ├── test_e2e.py        # Capa 3: Robot de Playwright (Navegación real en Swagger)
│   ├── tests.py           # Capa 1: Tests unitarios aislados de lógica y matemáticas
│   └── views.py           # Controladores REST API y manejo de excepciones de negocio
├── config/
│   ├── settings.py        # Configuración central del Framework, variables de entorno y Specs
│   └── urls.py            # Enrutador maestro virtual de endpoints y Swagger UI
├── scripts_sql/
│   └── 01_init_schema.sql # Scripts SQL puros con restricciones e índices para el DBA
├── screenshots/           # Evidencias visuales de interfaz capturadas por el robot Playwright
├── Dockerfile             # Configuración de compilación nativa Linux + Headless Chromium
├── docker-compose.yml     # Orquestador local de servicios, volúmenes de datos y red interna
├── entrypoint.sh          # Script bash de control de arranque y espera de servicios
└── requirements.txt       # Manifiesto de dependencias congeladas de Python
```

---

## 🔑 Configuración del Entorno Virtual (`.env`)

Crea un archivo llamado `.env` en la raíz del proyecto. Este archivo está protegido por el `.gitignore` y jamás debe subirse al control de versiones:

```env
# Configuración Básica de Django
DEBUG=True
SECRET_KEY=desarrollo_local_llave_altamente_insegura_12345

# Conexión Externa a Base de Datos (Neon Postgres)
DATABASE_URL=postgres://tu_usuario:tu_password@ep-tu-endpoint-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

## 🛠️ Instalación Paso a Paso (Entorno Local)

### Requisitos Previos
* Motor de Docker actualizado.
* Cliente Git.

### Ejecución del Entorno:

1. **Construir los Contenedores:**
   Compila la imagen limpia de Linux Bookworm e instala los binarios internos del navegador de pruebas:
   ```bash
   docker compose up -d --build
   ```

2. **Ejecutar Migraciones de Base de Datos:**
   Prepara la base de datos en Neon mapeando el esquema relacional de Django:
   ```bash
   docker compose exec backend python manage.py migrate
   ```

3. **Verificar Estado del Servicio:**
   Entra en tu navegador a `http://localhost:8000/api/docs/` para interactuar con la consola visual de Swagger UI.

---

## 🌱 Población Inicial de Datos (Seed/Fixtures)

Dado que el validador no puede procesar impuestos de un país que no existe en el sistema, debes cargar los datos base de Latinoamérica.

### Opción A: A través de Django Admin (Interfaz Gráfica)
1. Crea un usuario administrador ejecutando:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
2. Ingresa a `http://localhost:8000/admin/`, inicia sesión e ingresa los países en el módulo **Pais**.

### Opción B: Inyección SQL Directa (Recomendado para DBAs)
Utiliza el cliente de Neon o tu herramienta SQL favorita para ejecutar estas inserciones iniciales:
```sql
INSERT INTO api_pais (nombre, codigo_iso, tasa_impuesto) VALUES 
('Colombia', 'CO', 0.1900),
('Argentina', 'AR', 0.2100),
('Chile', 'CL', 0.1900),
('México', 'MX', 0.1600);
```

---

## 🛡️ Estrategia de Calidad: Búnker de Testing (10/10)

El pipeline de integración continua ejecuta de forma obligatoria la **Tríada Perfecta de Pruebas** en cada Pull Request:

```bash
docker compose exec backend python manage.py test api --keepdb
```

### Detalle de las Capas Evaluadas:
* **Pruebas de Negocio (Unit):** Evalúan que si un país tiene `0.19` de tasa, un monto de `100` devuelva exactamente `19`.
* **Pruebas de API (Integration):** Validan respuestas con payloads erróneos devolviendo `400 Bad Request` y payloads exitosos devolviendo `200 OK`.
* **Pruebas E2E (Playwright):** Un script asíncrono simula las acciones de un usuario real dentro de Chrome. Escribe en el Swagger, hace click en ejecutar, valida el estado de la UI y guarda una fotografía en la ruta local `screenshots/screenshot_endpoint_ejecutado.png`.

---

## 🔌 Documentación Extendida de Endpoints (JSON Payloads)

### 1. Calcular Impuesto (`POST /api/calcular-impuesto/`)
Procesa el cálculo financiero y genera la persistencia en el historial.

* **Estructura del Request Body (JSON):**
```json
{
  "codigo_iso": "CO",
  "monto": 1500.50
}
```
* **Estructura del Response Body (JSON - 200 OK):**
```json
{
  "id_registro": 42,
  "pais": "Colombia",
  "codigo_iso": "CO",
  "monto_original": 1500.50,
  "impuesto_calculado": 285.10,
  "total_con_impuesto": 1785.60,
  "fecha_operacion": "2026-05-28T16:30:00Z"
}
```

### 2. Listar Países Activos (`GET /api/paises/`)
Devuelve la matriz de configuración de tasas vigentes en el backend.

* **Estructura del Response Body (JSON - 200 OK):**
```json
[
  {
    "id": 1,
    "nombre": "Colombia",
    "codigo_iso": "CO",
    "tasa_impuesto": 0.19
  }
]
```

### 3. Historial de Auditoría (`GET /api/historial/`)
Endpoint optimizado para que **n8n** extraiga reportes de conciliación fiscal periódicos. Devuelve todos los cálculos cronológicamente.

---

## 🚀 Guía de Despliegue en Producción

### Checklist Obligatorio de Producción
1. Configurar `DEBUG=False` en el panel de control del servidor en la nube.
2. Registrar el dominio oficial en `ALLOWED_HOSTS`.
3. Inyectar la URL productiva de Neon mediante variables del sistema seguro del proveedor.

### Scripts de Inicialización Automatizados (Deploy Hooks)
En el servidor de producción, configura los siguientes comandos en secuencia para que se ejecuten automáticamente tras descargar el contenedor:

```bash
# Unificar archivos estáticos para la interfaz de Swagger UI
python manage.py collectstatic --noinput

# Ejecutar migraciones estructurales sobre la BD productiva de Neon
python manage.py migrate
```

---

## 🕵️‍♂️ Solución de Problemas Frecuentes (Troubleshooting)

### 1. Error: `playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist`
* **Causa:** Intentaste correr los tests en un contenedor desactualizado que no ha descargado los motores gráficos.
* **Solución:** Recompila forzando la purga total del caché local de imágenes:
  ```bash
  docker compose down
  docker compose build --no-cache backend
  docker compose up -d
  ```

### 2. Error: `django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context`
* **Causa:** Playwright ejecuta hilos asíncronos para emular el navegador y Django bloquea las conexiones a la base de datos por seguridad.
* **Solución:** Asegúrate de que tu archivo `api/test_e2e.py` tenga declarada la bandera de escape del sistema en el método de inicialización:
  ```python
  os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
  ```

### 3. Logs Sucios: `unable to guess serializer` en la consola
* **Causa:** Mensaje informativo de Swagger al encontrar vistas personalizadas (`APIViews`) que no tienen un serializador explícito en su definición base.
* **Solución:** El sistema funciona al 100%, pero si deseas logs limpios, añade el decorador `@extend_schema(responses=TuSerializer)` sobre el método HTTP correspondiente en el archivo `views.py`.