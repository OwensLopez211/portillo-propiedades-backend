# properties/apps.py
from django.apps import AppConfig

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        try:
            import os
            if os.environ.get('RUN_MAIN'):  # Evita la doble ejecución
                from . import schedulers
                schedulers.start()
        except ImportError:
            pass