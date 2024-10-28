from django.urls import path
from .views import get_token, unlink_mercadolibre, get_mercadolibre_items

urlpatterns = [
    path('get-token/', get_token, name='get_token'),  # URL para obtener el token
    path('mercadolibre/unlink', unlink_mercadolibre, name='unlink_mercadolibre'),
    path('mercadolibre/items/', get_mercadolibre_items, name='get-mercadolibre-items'),
]
