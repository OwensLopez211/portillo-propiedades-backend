from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .models import Agent, Property, PropertyImage,Region, Comuna, UFValue
from .serializers import PropertySerializer, AgentSerializer,RegionSerializer, ComunaSerializer
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
        featured_properties = Property.objects.filter(is_featured=True, is_published=True)
        serializer = PropertySerializer(featured_properties, many=True, context={'request': request})
        return Response(serializer.data)

# Vista para obtener la lista de propiedades con filtros (pública)
class PropertyListView(APIView):
    permission_classes = [AllowAny]  # Acceso público

    def get(self, request):
        # Obtener solo las propiedades publicadas para el sitio web público
        properties = Property.objects.all()

        # Filtros opcionales para búsqueda y ordenamiento
        search = request.GET.get('search')
        if search:
            properties = properties.filter(
                Q(title__icontains=search) | Q(tipo_propiedad__icontains=search)
            )

        # Filtrar por publicación si es necesario
        is_published = request.GET.get('is_published')
        if is_published is not None:
            properties = properties.filter(is_published=is_published.lower() == 'true')
            
        # Aplicar los filtros existentes...
        operation = request.GET.get('operation')
        if operation:
            properties = properties.filter(tipo_operacion=operation)

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
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info("Solicitud recibida para subir propiedades masivamente.")
        
        excel_file = request.FILES.get('excel')
        if not excel_file:
            return Response({"error": "No se subió un archivo Excel"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(excel_file, sheet_name='Plantilla_Propiedades', engine='openpyxl')
            print("Columnas leídas desde el archivo Excel:", df.columns.tolist())
        except Exception as e:
            return Response({"error": f"Error al leer el archivo Excel: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Procesar cada fila del Excel
        for index, row in df.iterrows():
            try:
                # Obtener el valor actual de UF
                valor_uf = Property.get_uf_value()

                # Convertir y validar coordenadas
                latitud = float(row['latitud']) if not pd.isna(row['latitud']) else None
                longitud = float(row['longitud']) if not pd.isna(row['longitud']) else None

                # Validar que las coordenadas estén dentro del rango permitido
                if latitud is not None and (latitud < -90 or latitud > 90):
                    raise ValueError(f"Latitud inválida en la fila {index + 2}: debe estar entre -90 y 90")
                if longitud is not None and (longitud < -180 or longitud > 180):
                    raise ValueError(f"Longitud inválida en la fila {index + 2}: debe estar entre -180 y 180")

                # Convertir valores decimales a float con redondeo
                superficie_total = round(float(row['superficie_total']), 2) if not pd.isna(row['superficie_total']) else None
                superficie_cubierta = round(float(row['superficie_cubierta']), 2) if not pd.isna(row['superficie_cubierta']) else None
                gastos_comunes = round(float(row['gastos_comunes']), 2) if not pd.isna(row['gastos_comunes']) else None
                contribuciones = round(float(row['contribuciones']), 2) if not pd.isna(row['contribuciones']) else None
                expensas = round(float(row['expensas']), 2) if not pd.isna(row['expensas']) else None

                # Convertir la moneda del Excel a la nomenclatura del modelo
                moneda_precio = 'UF' if str(row['moneda']).upper() == 'UF' else 'CLP'

                # Buscar el agente por ID
                agent = Agent.objects.get(id=row['agente_id']) if not pd.isna(row['agente_id']) else None

                # Buscar la región y la comuna
                region = Region.objects.get(id=row['region_id']) if not pd.isna(row['region_id']) else None
                comuna = Comuna.objects.get(nombre=row['comuna']) if not pd.isna(row['comuna']) else None

                # Crear la propiedad con los campos actualizados
                Property.objects.create(
                    title=str(row['title']),
                    tipo_propiedad=str(row['tipo_propiedad']),
                    descripcion=str(row['descripcion']),
                    direccion=str(row['direccion']),
                    region=region,
                    comuna=comuna,
                    ubicacion_referencia=str(row['ubicacion_referencia']) if not pd.isna(row['ubicacion_referencia']) else None,
                    precio_venta=int(row['precio_venta']) if not pd.isna(row['precio_venta']) else None,
                    precio_renta=int(row['precio_renta']) if not pd.isna(row['precio_renta']) else None,
                    moneda_precio=moneda_precio,
                    valor_uf_al_momento=valor_uf,
                    habitaciones=int(row['habitaciones']),
                    baños=int(row['baños']),
                    superficie_total=superficie_total,
                    superficie_cubierta=superficie_cubierta,
                    gastos_comunes=gastos_comunes,
                    contribuciones=contribuciones,
                    expensas=expensas,
                    latitud=latitud,
                    longitud=longitud,
                    agent=agent,
                    tipo_operacion=str(row['tipo_operacion']),
                    is_published=True
                )
                print(f"Propiedad creada exitosamente para la fila {index + 2}")

            except ValueError as e:
                return Response({
                    "error": f"Error en la fila {index + 2}: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "error": f"Error en la fila {index + 2}: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Propiedades subidas exitosamente"
        }, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def count_properties(request):
    property_count = Property.objects.count()
    return Response({'count': property_count})

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    # Endpoint para obtener comunas de una región específica
    @action(detail=True, methods=['get'])
    def comunas(self, request, pk=None):
        region = self.get_object()
        comunas = region.comunas.all()
        serializer = ComunaSerializer(comunas, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_latest_uf(request):
    try:
        latest_uf = UFValue.objects.latest('date')
        return Response({
            'value': float(latest_uf.value),
            'date': latest_uf.date,
            'formatted_value': f"$ {'{:,.2f}'.format(latest_uf.value)}"
        })
    except UFValue.DoesNotExist:
        return Response({
            'error': 'No hay valor UF disponible'
        }, status=404)
    
def obtener_uf_actual(request):
        """Endpoint para obtener el valor actual de la UF."""
        try:
            # Usar la lógica existente del modelo
            uf_value = Property.get_uf_value()
            return JsonResponse({'valor_uf': float(uf_value)}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)