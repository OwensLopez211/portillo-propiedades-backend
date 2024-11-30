from rest_framework import serializers
from .models import Property, PropertyImage, Agent, Region, Comuna

class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        # Comprobar si hay una imagen y si la URL está disponible
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None  # Retornar None si no hay imagen

class AgentSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ['id', 'name', 'role', 'phone', 'email', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj):
        # Comprobar si hay una imagen de perfil y si la URL está disponible
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None  # Retornar None si no hay imagen de perfil

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'nombre']

class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ['id', 'nombre']

class PropertySerializer(serializers.ModelSerializer):
    precio_venta_uf = serializers.SerializerMethodField()
    precio_renta_uf = serializers.SerializerMethodField()
    images = PropertyImageSerializer(many=True, read_only=True)
    
    # Campos adicionales para mostrar datos anidados
    agent_detail = AgentSerializer(source='agent', read_only=True)
    region_detail = RegionSerializer(source='region', read_only=True)
    comuna_detail = ComunaSerializer(source='comuna', read_only=True)

    # Campos de solo ID para creación y actualización
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())
    comuna = serializers.PrimaryKeyRelatedField(queryset=Comuna.objects.all())

    class Meta:
        model = Property
        fields = '__all__'