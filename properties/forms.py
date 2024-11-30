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
            'superficie_total',
            'superficie_cubierta',
            'expensas', 
            'latitud', #momentaneamente no ocupado
            'longitud', #momentaneamente no ocupado
            'agent',
            'is_featured',
            'tipo_operacion',
        ]

        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        tipo_operacion = cleaned_data.get("tipo_operacion")
        precio_venta = cleaned_data.get("precio_venta")
        precio_renta = cleaned_data.get("precio_renta")

        if tipo_operacion == 'venta' and not precio_venta:
            self.add_error('precio_venta', 'El precio de venta es obligatorio para propiedades en venta.')

        if tipo_operacion == 'arriendo' and not precio_renta:
            self.add_error('precio_renta', 'El precio de renta es obligatorio para propiedades en arriendo.')

        return cleaned_data

# Definición de PropertyImageFormSet
PropertyImageFormSet = modelformset_factory(PropertyImage, form=forms.ModelForm, extra=12, max_num=12, fields=('image',))
