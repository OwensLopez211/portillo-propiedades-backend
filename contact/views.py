from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.contrib import messages

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Envía el correo electrónico
            send_mail(
                f'Mensaje de {name}',  # Asunto del correo
                message,  # Cuerpo del correo
                email,  # De
                ['propiedadesportilla0@gmail.com'],  # Para
            )

            messages.success(request, '¡Gracias por contactarnos! Te responderemos pronto.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})
