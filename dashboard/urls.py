from django.urls import path
from .views import dashboard_view, add_property_view, edit_property_view, list_property_view, delete_property_view, upload_properties, delete_property_image

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),  # Define la URL para el dashboard
    path('add-property/', add_property_view, name='add-property'),
    path('edit-property/<int:property_id>/', edit_property_view, name='edit-property'),
    path('delete-property-image/<int:property_id>/<int:image_id>/', delete_property_image, name='delete-property-image'),
    path('delete-property/<int:property_id>/', delete_property_view, name='delete-property'),
    path('properties/', list_property_view, name='list-property'),
    path('upload-properties/', upload_properties, name='upload-properties'),
]
