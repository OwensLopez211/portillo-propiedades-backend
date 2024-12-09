from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import logging

logger = logging.getLogger(__name__)

# Referencia global para el scheduler
scheduler = None  


def start_scheduler_without_db_access():
    """
    Inicia el scheduler sin programar tareas que acceden a la base de datos.
    """
    global scheduler
    if scheduler and scheduler.running:
        print("El scheduler ya está corriendo.")
        return  # Evita inicialización duplicada

    try:
        print("Iniciando el scheduler...")
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.start()
        print("Scheduler iniciado correctamente.")
        logger.info("Scheduler iniciado sin tareas dependientes de la base de datos.")
    except Exception as e:
        print(f"Error al iniciar el scheduler: {e}")
        logger.error(f"Error iniciando el scheduler: {e}")


def schedule_tasks_with_db_access():
    """
    Programa tareas que requieren acceso a la base de datos.
    Este método debe llamarse después de que Django haya cargado completamente.
    """
    global scheduler
    if not scheduler or not scheduler.running:
        logger.warning("El scheduler no está iniciado. No se pueden programar tareas.")
        return

    try:
        from .tasks import actualizar_uf, actualizar_precios_clp  # Importa tareas aquí para evitar problemas de inicialización

        # Programar tarea para actualizar UF
        scheduler.add_job(
            actualizar_uf,
            'cron',
            hour=1,
            minute=0,
            name='actualizar_uf',
            jobstore='default',
            replace_existing=True
        )

        # Programar tarea para actualizar precios en CLP
        scheduler.add_job(
            actualizar_precios_clp,
            'cron',
            hour=1,
            minute=20,
            name='actualizar_precios_clp',
            jobstore='default',
            replace_existing=True
        )

        logger.info("Tareas programadas con acceso a la base de datos.")
    except Exception as e:
        logger.error(f"Error programando tareas con acceso a la base de datos: {e}")


def stop_scheduler():
    """
    Apaga el scheduler de forma segura.
    Este método se llama durante el apagado del servidor.
    """
    global scheduler
    if scheduler:
        try:
            scheduler.shutdown()
            logger.info("Scheduler apagado.")
        except Exception as e:
            logger.error(f"Error al apagar el scheduler: {e}")

def is_scheduler_running():
    """
    Verifica si el scheduler está activo.
    """
    global scheduler
    if scheduler and scheduler.running:
        logger.info("El scheduler está corriendo.")
        return True
    logger.warning("El scheduler NO está corriendo.")
    return False
