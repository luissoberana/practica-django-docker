# 1. Usar la imagen oficial de Python
FROM python:3.11-slim

# 2. Configurar variables de entorno para que Python sea rápido en producción
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer la carpeta de trabajo dentro del servidor
WORKDIR /app

# 4. Instalar las librerías del proyecto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código de nuestro proyecto a la carpeta del servidor
COPY . /app/

# 6. Exponer el puerto estándar de Render
EXPOSE 10000

# 7. Comando final: Aplicar migraciones automáticas y encender el servidor industrial Gunicorn
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:10000