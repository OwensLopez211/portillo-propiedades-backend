from django.urls import path
from .views import (
    AgentListCreateView,
    PropertyListCreateView, 
    PropertyDetailView, 
    FeaturedPropertiesAPIView, 
    PropertyListView)
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet

router = DefaultRouter()
router.register(r'agents', AgentViewSet)

urlpatterns = [
    path('agents/', AgentListCreateView.as_view(), name='agent-list-create'),
    path('properties/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('featured-properties/', FeaturedPropertiesAPIView.as_view(), name='featured-properties-api'),
    path('property-list/', PropertyListView.as_view(), name='property-list'),  # Esta es la URL que debería estar disponible.
]

urlpatterns += router.urls