# portillo_propiedades_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView 
from django.conf import settings
from django.conf.urls.static import static
from django.urls import get_resolver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', include('dashboard.urls')),  # Incluir la ruta del dashboard
    path('api/', include('properties.urls')),  # Las rutas de 'properties' estarán bajo el prefijo 'api/'
    path('contact/', include('contact.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Herramienta de depuración para imprimir todas las URL patterns
url_patterns = get_resolver().url_patterns

for pattern in url_patterns:
    try:
        print(pattern.pattern)
    except AttributeError:
        print(pattern)
