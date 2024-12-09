from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        """Inicia el scheduler al arrancar la aplicación."""
        import os
        if os.environ.get('RUN_MAIN'):  # Evita inicialización doble
            try:
                from properties.schedulers import start_scheduler_without_db_access
                start_scheduler_without_db_access()
                logger.info("Scheduler iniciado desde apps.py")
            except Exception as e:
                logger.error(f"Error iniciando el scheduler: {e}")
