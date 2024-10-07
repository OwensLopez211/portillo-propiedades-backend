# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import UserActionLog
# from properties.models import Property
# from django.contrib.auth.models import User

# @receiver(post_save, sender=Property)
# def log_property_save(sender, instance, created, **kwargs):
#     # Asegúrate de que el usuario no sea None antes de crear un log
#     if instance.created_by:
#         action = UserActionLog.CREATE if created else UserActionLog.UPDATE
#         UserActionLog.objects.create(user=instance.created_by, action_type=action, property=instance)

# @receiver(post_delete, sender=Property)
# def log_property_delete(sender, instance, **kwargs):
#     # Asegúrate de que el usuario no sea None antes de crear un log
#     if instance.created_by:
#         UserActionLog.objects.create(user=instance.created_by, action_type=UserActionLog.DELETE, property=instance)
