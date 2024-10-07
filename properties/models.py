from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import imghdr
from django.contrib.auth.models import User

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_image = models.ImageField(upload_to='agent_profiles/', null=True, blank=True)  # Campo para imagen de perfil

    def __str__(self):
        return self.name
    
# Modelo para Región
class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo para Comuna
class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='comunas')

    def __str__(self):
        return self.nombre

class Property(models.Model):
    # Opciones para tipo de operación
    VENTA = 'venta'
    ARRIENDO = 'arriendo'
    TIPO_OPERACION_CHOICES = [
        (VENTA, 'Venta'),
        (ARRIENDO, 'Arriendo'),
    ]

    # Definir los tipos de propiedad
    PROPERTY_TYPE_CHOICES = [
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('oficina', 'Oficina'),
        ('comercial', 'Comercial'),
        ('parcela', 'Parcela'),
        ('estacionamiento', 'Estacionamiento'),
        ('bodega', 'Bodega'),
        ('terreno', 'Terreno'),
    ]

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    tipo_propiedad = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, default='casa')
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_venta_uf = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Campo para UF de venta
    
    precio_renta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_renta_uf = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Campo para UF de arriendo
    
    habitaciones = models.IntegerField()
    baños = models.IntegerField()
    gastos_comunes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contribuciones = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    publicada = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    tipo_operacion = models.CharField(
        max_length=8,
        choices=TIPO_OPERACION_CHOICES,
        default=VENTA,  
    )

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"

    def clean(self):
        # Validación para permitir solo ciertos tipos de imagen
        if imghdr.what(self.image) not in ['jpeg', 'png', 'gif']:
            raise ValidationError('Solo se permiten archivos JPEG, PNG o GIF.')

    def delete(self, *args, **kwargs):
        # Elimina el archivo físico
        if self.image:
            print(f"Eliminando archivo físico: {self.image.path}")  # Mensaje de depuración
            self.image.delete(save=False)  # Elimina el archivo físico
        # Llama al método delete original
        super(PropertyImage, self).delete(*args, **kwargs)
