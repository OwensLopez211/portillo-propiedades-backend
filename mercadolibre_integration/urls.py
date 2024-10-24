from django.urls import path
from .views import get_token, unlink_mercadolibre

urlpatterns = [
    path('get-token/', get_token, name='get_token'),  # URL para obtener el token
    path('mercadolibre/unlink', unlink_mercadolibre, name='unlink_mercadolibre'),
]
