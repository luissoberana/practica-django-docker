#!/bin/sh

# Detener la ejecución si ocurre algún error intermedio
set -e

echo "🏥 [ENTRYPOINT] Iniciando comprobaciones del Validador de Impuestos..."

# 1. Aplicar las migraciones del ORM en Neon.tech
echo "🏗️ Aplicando migraciones en la base de datos de Neon..."
python manage.py migrate --noinput

# 2. Ejecutar tu comando personalizado para llenar los Países y sus impuestos
echo "📊 Verificando y poblation la tabla de países..."
python manage.py poblar_paises

# 3. Pasar el testigo al comando principal (Liberar el servidor web de desarrollo o producción)
echo "🚀 Todo listo. Entregando el control al servidor..."
exec "$@"