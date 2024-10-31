from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeletePropertyImageView,
    PropertyListCreateView, 
    PropertyDetailView,
    FeaturedPropertiesAPIView,
    PropertyListView,
    mercado_libre_callback,
    AgentViewSet,
    MassPropertyUploadView,
    count_properties,
    RegionViewSet  # Agrega el RegionViewSet
)

# Configuración del router para los agentes
router = DefaultRouter()
router.register(r'agents', AgentViewSet)
router.register(r'regions', RegionViewSet)  # Registra el RegionViewSet

# Definición de las URL patterns
urlpatterns = [
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),  # Listar y crear propiedades
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),  # Detalle, actualizar y eliminar propiedades
    path('featured-properties/', FeaturedPropertiesAPIView.as_view(), name='featured-properties-api'),  # Propiedades destacadas
    path('property-list/', PropertyListView.as_view(), name='property-list'),  # Listar propiedades con filtros
    path('property-images/<int:pk>/', DeletePropertyImageView.as_view(), name='delete-property-image'),  # Eliminar imágenes
    path('notifications/callback/', mercado_libre_callback, name='mercado_libre_callback'),  # Callback de notificaciones de MercadoLibre
    path('upload-mass-properties/', MassPropertyUploadView.as_view(), name='upload_mass_properties'),
    path('count/', count_properties, name='count_properties'),
]

# Agregar las rutas del router (para agentes y regiones)
urlpatterns += router.urls
