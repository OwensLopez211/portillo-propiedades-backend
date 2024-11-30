# properties/schedulers.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
import requests
from decimal import Decimal
from datetime import datetime
from .models import UFValue, Property

def actualizar_uf():
    try:
        response = requests.get('https://mindicador.cl/api/uf')
        if response.status_code == 200:
            data = response.json()
            latest_uf = data['serie'][0]
            
            fecha = datetime.strptime(
                latest_uf['fecha'].split('T')[0],
                '%Y-%m-%d'
            ).date()
            
            UFValue.objects.update_or_create(
                date=fecha,
                defaults={'value': Decimal(str(latest_uf['valor']))}
            )
            print(f"UF actualizada: {latest_uf['valor']} para fecha {fecha}")
    except Exception as e:
        print(f"Error actualizando UF: {str(e)}")

def actualizar_precios_clp():
    """Actualiza los precios en CLP para todas las propiedades con precios en UF."""
    try:
        # Obtiene el valor más reciente de la UF
        uf_value = UFValue.objects.first()
        if not uf_value:
            print("No hay valores de UF disponibles para actualizar precios.")
            return

        # Recorre propiedades que tienen precios en UF
        propiedades = Property.objects.filter(moneda_precio='UF')
        for propiedad in propiedades:
            if propiedad.precio_venta:
                propiedad.precio_venta = round(propiedad.precio_venta * uf_value.value, 2)
            if propiedad.precio_renta:
                propiedad.precio_renta = round(propiedad.precio_renta * uf_value.value, 2)
            propiedad.save()

        print(f"Precios en CLP actualizados para {propiedades.count()} propiedades.")
    except Exception as e:
        print(f"Error actualizando precios en CLP: {str(e)}")

def start():
    """Inicia el scheduler con las tareas programadas."""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Actualiza el valor de la UF todos los días a la 1:00 AM
    scheduler.add_job(
        actualizar_uf,
        'cron',
        hour=1,
        minute=0,
        name='actualizar_uf',
        jobstore='default'
    )

    # Actualiza los precios en CLP todos los días a la 1:05 AM (después de actualizar la UF)
    scheduler.add_job(
        actualizar_precios_clp,
        'cron',
        hour=1,
        minute=20,
        name='actualizar_precios_clp',
        jobstore='default'
    )
    
    scheduler.start()