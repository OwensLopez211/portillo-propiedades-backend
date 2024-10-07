# contact/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nombre')
    lastname = forms.CharField(max_length=100, label='Apellidos')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Teléfono')
    message = forms.CharField(widget=forms.Textarea, label='Comentario')
