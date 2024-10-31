# properties/management/commands/populate_regions_comunas.py
import json
from django.core.management.base import BaseCommand
from properties.models import Region, Comuna

class Command(BaseCommand):
    help = 'Popula la base de datos con regiones y comunas de Chile'

    def handle(self, *args, **options):
        # Cargar el archivo JSON con los datos
        with open('data/regiones_comunas.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Iterar sobre la lista de regiones en el JSON
        for item in data["regiones"]:  # Aquí se accede a la clave "regiones"
            region_name = item['region']
            comunas = item['comunas']

            # Crear o recuperar la región
            region, created = Region.objects.get_or_create(nombre=region_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Región creada: {region_name}'))

            # Crear comunas para la región
            for comuna_name in comunas:
                comuna, comuna_created = Comuna.objects.get_or_create(nombre=comuna_name, region=region)
                if comuna_created:
                    self.stdout.write(self.style.SUCCESS(f'  Comuna creada: {comuna_name} en {region_name}'))

        self.stdout.write(self.style.SUCCESS('Datos de regiones y comunas poblados correctamente.'))
