# properties/tasks.py
from django.core.management.base import BaseCommand
from .models import UFValue
import requests
from datetime import datetime

def update_uf_value():
    try:
        response = requests.get('https://mindicador.cl/api/uf')
        if response.status_code == 200:
            data = response.json()
            uf_value = data['serie'][0]['valor']
            date = datetime.strptime(data['serie'][0]['fecha'].split('T')[0], '%Y-%m-%d').date()
            
            UFValue.objects.update_or_create(
                date=date,
                defaults={'value': uf_value}
            )
            return True
    except Exception as e:
        print(f"Error actualizando valor UF: {e}")
        return False