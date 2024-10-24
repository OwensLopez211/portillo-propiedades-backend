from django.urls import path
from .views import get_token

urlpatterns = [
    path('get-token/', get_token, name='get_token'),  # URL para obtener el token
]
