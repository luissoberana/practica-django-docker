from django.core.management.base import BaseCommand
from api.models import Pais

class Command(BaseCommand):
    help = 'Puebla la base de datos con los países iniciales y sus impuestos'

    def handle(self, *args, **kwargs):
        # Lista de países de prueba con sus porcentajes reales (ej: 19% = 19.00)
        paises_data = [
            {'nombre': 'Colombia', 'codigo_iso': 'CO', 'porcentaje_impuesto': 19.00},
            {'nombre': 'Chile', 'codigo_iso': 'CL', 'porcentaje_impuesto': 19.00},
            {'nombre': 'Argentina', 'codigo_iso': 'AR', 'porcentaje_impuesto': 21.00},
            {'nombre': 'Perú', 'codigo_iso': 'PE', 'porcentaje_impuesto': 18.00},
            {'nombre': 'México', 'codigo_iso': 'MX', 'porcentaje_impuesto': 16.00},
        ]

        self.stdout.write('Poblando países en Neon.tech...')

        for data in paises_data:
            # 'get_or_create' busca si el país ya existe por su código ISO.
            # Si no existe, lo crea. Esto evita que los datos se dupliquen si corres el comando dos veces.
            pais, created = Pais.objects.get_or_create(
                codigo_iso=data['codigo_iso'],
                defaults={
                    'nombre': data['nombre'],
                    'porcentaje_impuesto': data['porcentaje_impuesto']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Creado: {data["nombre"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Ya existía: {data["nombre"]}'))

        self.stdout.write(self.style.SUCCESS('¡Proceso de población terminado!'))