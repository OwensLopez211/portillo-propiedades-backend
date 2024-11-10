# portillo_propiedades_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import get_resolver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('properties.urls')), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/contact/', include('contact.urls')),
    path('', include('users.urls')),  # Incluir las rutas de 'users'
    path('mercadolibre/', include('mercadolibre_integration.urls')),  # Incluye las rutas de 'mercadolibre_integration'
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Herramienta de depuración para imprimir todas las URL patterns
url_patterns = get_resolver().url_patterns

for pattern in url_patterns:
    try:
        print(pattern.pattern)
    except AttributeError:
        print(pattern)
