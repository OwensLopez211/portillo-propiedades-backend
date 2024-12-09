from decimal import Decimal
from datetime import datetime
import requests
import logging
from .models import UFValue, Property

logger = logging.getLogger(__name__)

def actualizar_uf():
    """Actualiza el valor de la UF desde la API externa."""
    try:
        print("Iniciando actualización de UF...")
        response = requests.get('https://mindicador.cl/api/uf')
        print(f"Estado de la respuesta: {response.status_code}")
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
        else:
            print(f"No se pudo obtener el valor UF. Código de respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error actualizando UF: {str(e)}")


def actualizar_precios_clp():
    """Actualiza los precios en CLP de las propiedades con precio en UF."""
    try:
        # Obtiene el valor más reciente de la UF
        uf_value = UFValue.objects.first()
        if not uf_value:
            logger.warning("No hay valores de UF disponibles para actualizar precios.")
            return

        # Itera sobre propiedades con moneda 'UF' y actualiza precios
        propiedades = Property.objects.filter(moneda_precio='UF')
        for propiedad in propiedades:
            if propiedad.precio_venta:
                propiedad.precio_venta = round(propiedad.precio_venta * uf_value.value, 2)
            if propiedad.precio_renta:
                propiedad.precio_renta = round(propiedad.precio_renta * uf_value.value, 2)
            propiedad.save()

        logger.info(f"Precios en CLP actualizados para {propiedades.count()} propiedades.")
    except Exception as e:
        logger.error(f"Error actualizando precios en CLP: {str(e)}")
