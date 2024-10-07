from rest_framework import serializers
from .models import Property, PropertyImage, Agent

class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

class AgentSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ['id', 'name', 'role', 'phone', 'email', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.profile_image.url) if obj.profile_image and request else obj.profile_image.url

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    agent = AgentSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'  # Incluye todos los campos, incluyendo 'agent' y 'images'
