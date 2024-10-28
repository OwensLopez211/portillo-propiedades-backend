from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .models import Agent, Property, PropertyImage, Comuna
from .serializers import PropertySerializer, AgentSerializer
import cloudinary.uploader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)

# Vista para listar y crear agentes (solo accesible por administradores)
class AgentListCreateView(generics.ListCreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAdminUser]  # Solo accesible por administradores

# Vista para manejo de agentes (CRUD) a través de un ViewSet (solo administradores)
class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAdminUser]  # Solo accesible por administradores

# Vista para listar y crear propiedades (solo accesible por usuarios autenticados)
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        agent_id = request.data.get('agent')  # Obtener el ID del agente

        # Si hay un agente asignado, asegúrate de que existe en la base de datos
        agent = None
        if agent_id:
            try:
                agent = Agent.objects.get(id=agent_id)
            except Agent.DoesNotExist:
                return Response({"error": "Agente no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Guarda la nueva propiedad en la base de datos, asignando el agente
            property_instance = serializer.save(agent=agent)

            # Manejar la carga de imágenes, si se han subido
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    # Crear la imagen y asociarla a la propiedad
                    PropertyImage.objects.create(property=property_instance, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Vista para editar y eliminar propiedades. Incluyendo sus imagenes asociadas a Cloudinary
class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        # Obtén la instancia de la propiedad que se va a actualizar
        property_instance = self.get_object()
        serializer = self.get_serializer(property_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Guarda los datos actualizados de la propiedad
            serializer.save()

            # Manejar las imágenes a eliminar
            images_to_delete = request.data.get('imagesToDelete', [])
            if images_to_delete:
                images_to_delete = json.loads(images_to_delete)  # Convertir el JSON a lista
                for image_id in images_to_delete:
                    try:
                        image = PropertyImage.objects.get(id=image_id)
                        cloudinary.uploader.destroy(image.image.public_id)  # Eliminar de Cloudinary
                        image.delete()  # Eliminar de la base de datos
                    except PropertyImage.DoesNotExist:
                        continue

            # **Manejo de nuevas imágenes**: Asegúrate de procesar las imágenes nuevas
            new_images = request.FILES.getlist('images')  # 'images' debe ser el nombre del campo en el formulario
            for image in new_images:
                # Crear una nueva instancia de PropertyImage y asociarla con la propiedad
                PropertyImage.objects.create(property=property_instance, image=image)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        # Obtén la instancia de la propiedad que se va a eliminar
        property_instance = self.get_object()

        try:
            # Asumiendo que las imágenes están relacionadas mediante una ForeignKey en el modelo PropertyImage
            property_images = property_instance.images.all()
            print(f"Imágenes a eliminar: {property_images}")

            # Elimina cada imagen manualmente usando el public_id de Cloudinary
            for image in property_images:
                public_id = image.image.public_id  # Obtén el public_id del objeto CloudinaryField
                print(f"Eliminando imagen de Cloudinary: {public_id}")
                cloudinary.uploader.destroy(public_id)  # Elimina la imagen de Cloudinary
                image.delete()  # Elimina la instancia de la imagen de la base de datos

            # Luego, elimina la propiedad
            property_instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            print(f"Error al eliminar la propiedad: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Vista para obtener propiedades destacadas (pública)
class FeaturedPropertiesAPIView(APIView):
    permission_classes = [AllowAny]  # Acceso público

    def get(self, request):
        featured_properties = Property.objects.filter(is_featured=True)
        serializer = PropertySerializer(featured_properties, many=True, context={'request': request})
        return Response(serializer.data)

# Vista para obtener la lista de propiedades con filtros (pública)
class PropertyListView(APIView):
    permission_classes = [AllowAny]  # Acceso público

    def get(self, request):
        properties = Property.objects.all()

        # Filtrar por operación (venta/arriendo)
        operation = request.GET.get('operation')
        print(f"Filtrando por operación: {operation}")
        if operation:
            properties = properties.filter(tipo_operacion=operation)

        # Filtrar por tipo de propiedad
        property_type = request.GET.get('propertyType')
        print(f"Filtrando por tipo de propiedad: {property_type}")
        if property_type:
            properties = properties.filter(tipo_propiedad=property_type)

        # Filtrar por comuna
        comuna = request.GET.get('comuna')
        print(f"Filtrando por comuna: {comuna}")
        if comuna:
            properties = properties.filter(comuna__nombre__icontains=comuna)

        # Filtrar por precio mínimo
        price_min = request.GET.get('priceMin')
        print(f"Filtrando por precio mínimo: {price_min}")
        if price_min:
            properties = properties.filter(Q(precio_venta__gte=price_min) | Q(precio_renta__gte=price_min))

        # Filtrar por precio máximo
        price_max = request.GET.get('priceMax')
        print(f"Filtrando por precio máximo: {price_max}")
        if price_max:
            properties = properties.filter(Q(precio_venta__lte=price_max) | Q(precio_renta__lte=price_max))

        # Serializa y envía la respuesta
        serializer = PropertySerializer(properties, many=True, context={'request': request})
        print(f"Propiedades encontradas: {serializer.data}")
        return Response(serializer.data)

# Eliminar independientemente la imagen de Cloudinaryen al Editar propiedad
class DeletePropertyImageView(generics.DestroyAPIView):
    queryset = PropertyImage.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            image = self.get_object()  # Obtener la imagen por ID (pk)
            image.delete()  # Eliminar la imagen de la base de datos y Cloudinary
            return Response({'message': 'Imagen eliminada correctamente'}, status=status.HTTP_204_NO_CONTENT)
        except PropertyImage.DoesNotExist:
            return Response({'error': 'Imagen no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
# Vista para manejar las notificaciones de MercadoLibre
@csrf_exempt  # Para evitar la verificación CSRF en solicitudes externas
def mercado_libre_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Procesar el cuerpo de la solicitud
            logger.info(f'Datos recibidos de MercadoLibre: {data}')  # Loguear la data recibida

            # Aquí podrías manejar diferentes tipos de notificaciones
            event_type = data.get('topic')
            if event_type == 'orders':
                logger.info('Nueva orden recibida de MercadoLibre')
                # Lógica para manejar órdenes
            elif event_type == 'questions':
                logger.info('Nueva pregunta recibida en MercadoLibre')
                # Lógica para manejar preguntas
            else:
                logger.warning(f'Tipo de evento no manejado: {event_type}')

            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            logger.error('Formato de datos JSON inválido')
            return JsonResponse({'error': 'Invalid data format'}, status=400)
    logger.warning(f'Método HTTP no permitido: {request.method}')
    return JsonResponse({'error': 'Invalid request method'}, status=405)

class MassPropertyUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # Para manejar archivos en la solicitud
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # Verificar si hay un archivo CSV
        csv_file = request.FILES.get('csv')
        if not csv_file:
            return Response({"error": "No se subió un archivo CSV"}, status=status.HTTP_400_BAD_REQUEST)

        # Leer el archivo CSV
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return Response({"error": f"Error al leer el archivo CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Procesar cada fila del CSV
        for index, row in df.iterrows():
            try:
                # Buscar el agente por ID (si aplica)
                agent = Agent.objects.get(id=row['agente_id']) if 'agente_id' in row and not pd.isna(row['agente_id']) else None
                # Buscar la comuna por nombre (si aplica)
                comuna = Comuna.objects.get(nombre=row['comuna']) if 'comuna' in row and not pd.isna(row['comuna']) else None

                # Crear la propiedad
                Property.objects.create(
                    title=row['titulo'],
                    tipo_propiedad=row['tipo_propiedad'],
                    descripcion=row['descripcion'],
                    direccion=row['direccion'],
                    precio_venta=row['precio_venta'] if not pd.isna(row['precio_venta']) else None,
                    precio_renta=row['precio_renta'] if not pd.isna(row['precio_renta']) else None,
                    moneda=row['moneda'],
                    habitaciones=row['habitaciones'],
                    baños=row['baños'],
                    superficie_total=row['superficie_total'] if not pd.isna(row['superficie_total']) else None,
                    superficie_cubierta=row['superficie_cubierta'] if not pd.isna(row['superficie_cubierta']) else None,
                    gastos_comunes=row['gastos_comunes'] if not pd.isna(row['gastos_comunes']) else None,
                    contribuciones=row['contribuciones'] if not pd.isna(row['contribuciones']) else None,
                    expensas=row['expensas'] if not pd.isna(row['expensas']) else None,
                    latitud=row['latitud'] if not pd.isna(row['latitud']) else None,
                    longitud=row['longitud'] if not pd.isna(row['longitud']) else None,
                    agent=agent,
                    comuna=comuna,
                    tipo_operacion=row['tipo_operacion']
                )
            except Exception as e:
                return Response({"error": f"Error al crear la propiedad en la fila {index}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Propiedades subidas exitosamente"}, status=status.HTTP_201_CREATED)
