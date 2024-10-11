from django import forms
from .models import Property, PropertyImage
from django.forms import modelformset_factory

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 
            'tipo_propiedad',
            'descripcion',
            'direccion',
            'region',       
            'comuna',      
            'precio_venta',
            'precio_renta',
            'habitaciones',
            'baños',
            'gastos_comunes',
            'contribuciones',
            'agent',
            'is_featured',
            'tipo_operacion',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }

# Definición de PropertyImageFormSet
PropertyImageFormSet = modelformset_factory(PropertyImage, form=forms.ModelForm, extra=12, max_num=12, fields=('image',))
