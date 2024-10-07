from rest_framework import generics, viewsets, status
from .models import Agent, Property
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import PropertySerializer, AgentSerializer

class AgentListCreateView(generics.ListCreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class FeaturedPropertiesAPIView(APIView):
    def get(self, request):
        featured_properties = Property.objects.filter(is_featured=True)
        serializer = PropertySerializer(featured_properties, many=True, context={'request': request})
        return Response(serializer.data)

class PropertyListView(APIView):
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
            properties = properties.filter(comuna__icontains=comuna)

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
