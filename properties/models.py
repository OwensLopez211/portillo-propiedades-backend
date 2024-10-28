from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import cloudinary.uploader
from cloudinary.models import CloudinaryField  



class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    profile_image = CloudinaryField('image', null=True, blank=True)

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
    ARRIENDO_TEMPORAL = 'arriendo_temporal'
    TIPO_OPERACION_CHOICES = [
        (VENTA, 'Venta'),
        (ARRIENDO, 'Arriendo'),
        (ARRIENDO_TEMPORAL, 'Arriendo Temporal')
    ]

    # Definir los tipos de propiedad
    PROPERTY_TYPE_CHOICES = [
        ('departamento', 'Departamentos'),
        ('casa', 'Casas'),
        ('oficina', 'Oficinas'),
        ('parcela', 'Parcelas'),
        ('local', 'Locales'),
        ('terreno', 'Terrenos'),
        ('sitio', 'Sitios'),
        ('bodega', 'Bodegas'),
        ('industrial', 'Industriales'),
        ('agricola', 'Agrícolas'),
        ('otros_inmuebles', 'Otros Inmuebles'),
        ('estacionamiento', 'Estacionamientos'),
        ('loteo', 'Loteos'),
        ('lotes_de_cementerio', 'Lotes de Cementerio'),
    ]

    mercadolibre_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    tipo_propiedad = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, default='casa')
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    
    # Campos de precio
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_renta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    moneda = models.CharField(max_length=3, default='CLP')  # Campo adicional para moneda (ejemplo: CLP, USD)

    # Información de la propiedad
    habitaciones = models.IntegerField()
    baños = models.IntegerField()
    ambientes = models.IntegerField(default=1)  # Para compatibilidad con Mercado Libre (total de espacios)
    superficie_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Superficie total en m2
    superficie_cubierta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Superficie cubierta en m2
    
    gastos_comunes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contribuciones = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expensas = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Equivalente de gastos comunes
    
    # Ubicación geográfica (para Mercado Libre)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    publicada = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    tipo_operacion = models.CharField(
        max_length=50,
        choices=TIPO_OPERACION_CHOICES,
        default=VENTA,
    )

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')

    def __str__(self):
        return f"Image for {self.property.title}"

# Método delete personalizado
    def delete(self, *args, **kwargs):
        # Verifica que haya una imagen antes de intentar eliminarla
        if self.image:
            print(f"Eliminando imagen de Cloudinary con public_id: {self.image.public_id}")  # Log para verificar
            cloudinary.uploader.destroy(self.image.public_id)  # Elimina la imagen de Cloudinary usando el public_id
        # Llama al delete original para que Django elimine la instancia de la base de datos
        super(PropertyImage, self).delete(*args, **kwargs)
