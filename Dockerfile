# 1. Base ultra-estable congelada en Debian 12 (Bookworm)
FROM python:3.11-slim-bookworm

# 2. Configurar variables de entorno para que Python sea rápido
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar las librerías del proyecto (incluye Playwright de Python)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código de nuestro proyecto a la carpeta del contenedor
COPY . /app/

# =====================================================================
# 🚀 INSTALACIÓN AUTOMÁTICA DE NAVEGADORES Y DEPENDENCIAS
# =====================================================================
COPY entrypoint.sh /entrypoint.sh

# Primero instalamos dos2unix (necesario para el entrypoint).
# Luego, le decimos a Playwright que descargue Chromium Y que instale 
# automáticamente las dependencias del sistema exactas que Bookworm necesita.
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix \
    && playwright install --with-deps chromium \
    && dos2unix /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/entrypoint.sh"]

# 6. Exponer el puerto estándar de tu Django
EXPOSE 8000

# 7. Comando final por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]