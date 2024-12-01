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
            # Leer el Excel ignorando filas vacías
            df = pd.read_excel(
                excel_file, 
                engine='openpyxl',
                skiprows=0,  # No saltamos la primera fila porque es el encabezado
                na_filter=True  # Mantener el filtrado de valores NA/vacíos
            )
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            print(f"Total de filas leídas (sin contar vacías): {len(df)}")
            print("Columnas encontradas:", df.columns.tolist())
            
            propiedades_creadas = 0
            errores = []

            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    print(f"\nProcesando fila {index + 2}:")
                    
                    # Verificar si la fila tiene datos
                    if pd.isna(row['codigo']) or pd.isna(row['title']):
                        continue  # Saltar filas sin código o título
                        
                    print(f"Código: {row['codigo']}, Título: {row['title']}")

                    # Verificar duplicados
                    if Property.objects.filter(codigo=str(row['codigo'])).exists():
                        errores.append(f"Fila {index + 2}: Ya existe una propiedad con el código {row['codigo']}")
                        continue

                    # Obtener el valor actual de UF
                    valor_uf = Property.get_uf_value()

                    # Procesar precios
                    precio_venta = None
                    precio_renta = None
                    
                    if not pd.isna(row['precio_venta']):
                        precio_venta = int(float(row['precio_venta']))
                    if not pd.isna(row['precio_renta']):
                        precio_renta = int(float(row['precio_renta']))

                    # Crear la propiedad
                    Property.objects.create(
                        codigo=str(row['codigo']),
                        title=str(row['title']),
                        tipo_propiedad=str(row['tipo_propiedad']),
                        descripcion=str(row['descripcion']) if not pd.isna(row['descripcion']) else "",
                        direccion=str(row['direccion']),
                        region=Region.objects.get(id=int(row['region_id'])) if not pd.isna(row['region_id']) else None,
                        comuna=Comuna.objects.get(nombre=str(row['comuna'])) if not pd.isna(row['comuna']) else None,
                        ubicacion_referencia=str(row['ubicacion_referencia']) if not pd.isna(row['ubicacion_referencia']) else None,
                        precio_venta=precio_venta,
                        precio_renta=precio_renta,
                        moneda_precio='UF' if str(row['moneda']).upper().strip() == 'UF' else 'CLP',
                        valor_uf_al_momento=valor_uf,
                        habitaciones=int(row['habitaciones']) if not pd.isna(row['habitaciones']) else 0,
                        baños=int(row['baños']) if not pd.isna(row['baños']) else 0,
                        superficie_total=float(row['superficie_total']) if not pd.isna(row['superficie_total']) else None,
                        superficie_cubierta=float(row['superficie_cubierta']) if not pd.isna(row['superficie_cubierta']) else None,
                        gastos_comunes=float(row['gastos_comunes']) if not pd.isna(row['gastos_comunes']) else None,
                        contribuciones=float(row['contribuciones']) if not pd.isna(row['contribuciones']) else None,
                        expensas=float(row['expensas']) if not pd.isna(row['expensas']) else None,
                        latitud=float(row['latitud']) if not pd.isna(row['latitud']) else None,
                        longitud=float(row['longitud']) if not pd.isna(row['longitud']) else None,
                        agent=Agent.objects.get(id=int(row['agente_id'])) if not pd.isna(row['agente_id']) else None,
                        tipo_operacion=str(row['tipo_operacion']),
                        is_published=True  # Por defecto publicada
                    )
                    propiedades_creadas += 1
                    print(f"✓ Propiedad creada exitosamente: {row['codigo']}")

                except Exception as e:
                    error_msg = f"Error en fila {index + 2}: {str(e)}"
                    print(f"✗ {error_msg}")
                    errores.append(error_msg)
                    continue

            # Preparar respuesta
            resumen = {
                "message": "Proceso completado",
                "total_filas_procesadas": len(df),
                "propiedades_creadas": propiedades_creadas,
                "propiedades_con_error": len(errores),
                "errores": errores if errores else None
            }

            return Response(resumen, 
                          status=status.HTTP_201_CREATED if propiedades_creadas > 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error general: {str(e)}")
            return Response({
                "error": f"Error al procesar el archivo: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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