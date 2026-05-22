# 1. Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Configuraciones para que Python funcione rápido y muestre errores en consola
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# 3. Le decimos a Docker que trabaje en una carpeta interna llamada /app
WORKDIR /app

# 4. Instalamos herramientas necesarias para la base de datos que usaremos después
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

# 5. Copiamos nuestro archivo de requerimientos a la carpeta /app
COPY requirements.txt /app/

# 6. Le decimos a Python que instale las librerías
RUN pip install --no-cache-dir -r requirements.txt

# 7. Finalmente, copiamos todo nuestro código adentro del contenedor
COPY . /app/