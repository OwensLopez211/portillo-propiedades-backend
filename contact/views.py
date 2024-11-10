from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings

@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_correo_api(request):
    print("Contenido de request.data:", request.data)  # Imprime para depuración

    data = request.data
    nombre = data.get('nombre')
    email = data.get('email')
    mensaje = data.get('mensaje')
    asunto = data.get('asunto', f'Nuevo mensaje de {nombre}')  # Usa el asunto proporcionado o crea uno predeterminado

    # Verifica que todos los campos necesarios estén presentes
    if not nombre or not email or not mensaje:
        return JsonResponse({'error': 'Todos los campos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    # Construye el mensaje del correo
    mensaje_correo = f'Nombre: {nombre}\nCorreo: {email}\n\nMensaje:\n{mensaje}'

    try:
        send_mail(
            asunto,  # Usa el asunto proporcionado o el predeterminado
            mensaje_correo,
            settings.DEFAULT_FROM_EMAIL,
            [settings.TARGET_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'mensaje': 'Correo enviado exitosamente'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': 'No se pudo enviar el correo', 'detalles': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
