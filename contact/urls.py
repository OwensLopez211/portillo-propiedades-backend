# contact/urls.py
from django.urls import path
from .views import enviar_correo_api


urlpatterns = [
    path('enviar-correo/', enviar_correo_api, name='enviar_correo_api'),
]
