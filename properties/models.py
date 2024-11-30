from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import requests
from django.http import JsonResponse
from datetime import datetime
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
    

class UFValue(models.Model):
    date = models.DateField(unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"UF {self.date}: ${self.value}"

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
    MONEDA_CLP = 'CLP'
    MONEDA_UF = 'UF'
    MONEDA_CHOICES = [
        (MONEDA_CLP, 'CLP'),
        (MONEDA_UF, 'UF'),
    ]

    moneda_precio = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default=MONEDA_CLP,
        help_text="Selecciona si el precio principal está en CLP o UF"
    )
    
    is_published = models.BooleanField(
        default=True,
        verbose_name="Publicada",
        help_text="Indica si la propiedad está visible en el sitio web"
    )   


    mercadolibre_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    ubicacion_referencia = models.CharField(max_length=255, blank=True, null=True, help_text="Ubicación de referencia para la propiedad")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    tipo_propiedad = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, default='casa')
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    
    # Campos de precio
    precio_venta = models.IntegerField( null=True, blank=True)
    precio_renta = models.IntegerField( null=True, blank=True)
    valor_uf_al_momento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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

    @staticmethod
    def get_uf_value():
        """Obtiene el valor actual de la UF desde mindicador.cl o la base de datos."""
        try:
            # Primero intenta obtener el valor más reciente en la base de datos
            uf = UFValue.objects.filter(date=timezone.now().date()).first()
            if uf:
                return uf.value

            # Si no existe en la base de datos, consulta la API
            response = requests.get('https://mindicador.cl/api/uf')
            if response.status_code == 200:
                data = response.json()
                # La API devuelve los valores ordenados por fecha, toma el más reciente
                latest_uf = data['serie'][0]
                uf_value = Decimal(str(latest_uf['valor']))

                # Convertir la fecha desde el formato de la API
                fecha = datetime.strptime(latest_uf['fecha'].split('T')[0], '%Y-%m-%d').date()

                # Guardar el valor en la base de datos si no existe
                UFValue.objects.get_or_create(date=fecha, defaults={'value': uf_value})

                return uf_value

            # Si falla la API, devuelve un valor por defecto
            return Decimal('35000')  # Valor fijo por si no se puede obtener
        except Exception as e:
            # Registrar el error para depuración
            print(f"Error al obtener el valor de la UF: {e}")
            return Decimal('35000')  # Valor por defecto en caso de error

    @property
    def precio_venta_alternativo(self):
        """Calcula el precio alternativo."""
        if self.precio_venta:
            if self.moneda_precio == self.MONEDA_UF:
                return round(self.precio_venta * self.get_uf_value(), 2)
            elif self.moneda_precio == self.MONEDA_CLP:
                return round(self.precio_venta / self.get_uf_value(), 2)
        return None

    def save(self, *args, **kwargs):
        self.valor_uf_al_momento = self.get_uf_value()
        super().save(*args, **kwargs)

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
