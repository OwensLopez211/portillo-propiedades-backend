#Esto es solo para poblar la base de datos con las regiones y comunas. 
#Eliminar despues!!


import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portillo_propiedades_backend.settings')
django.setup()

import json
from properties.models import Region, Comuna

def run():
    # Abrir y leer el archivo JSON
    try:
        with open('regiones_comunas.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Archivo JSON cargado correctamente. Total de regiones: {len(data['regiones'])}")
    except FileNotFoundError:
        print("Error: No se encontró el archivo JSON.")
        return
    except json.JSONDecodeError:
        print("Error: El archivo JSON no tiene un formato válido.")
        return

    # Iterar sobre las regiones y comunas
    for region_data in data['regiones']:
        region_name = region_data['region']
        print(f"Procesando región: {region_name}")
        
        # Crear o obtener la región
        region_instance, created = Region.objects.get_or_create(nombre=region_name)
        if created:
            print(f"Región creada: {region_name}")
        else:
            print(f"Región ya existente: {region_name}")
        
        # Iterar sobre las comunas de la región
        for comuna_name in region_data['comunas']:
            # Crear o obtener la comuna y asociarla con la región
            comuna_instance, created = Comuna.objects.get_or_create(nombre=comuna_name, region=region_instance)
            if created:
                print(f"Comuna creada: {comuna_name}")
            else:
                print(f"Comuna ya existente: {comuna_name}")
    
    print("Regiones y comunas cargadas exitosamente.")
