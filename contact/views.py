from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_correo_api(request):
    try:
        logger.info("Received email request")
        logger.debug(f"Request data: {request.data}")

        data = request.data
        nombre = data.get('nombre')
        email = data.get('email')
        mensaje = data.get('mensaje')
        asunto = data.get('asunto', f'Nuevo mensaje de {nombre}')

        # Validate required fields
        if not all([nombre, email, mensaje]):
            logger.warning("Missing required fields")
            return JsonResponse({
                'error': 'Todos los campos son requeridos',
                'received_data': data
            }, status=status.HTTP_400_BAD_REQUEST)

        mensaje_correo = f'Nombre: {nombre}\nCorreo: {email}\n\nMensaje:\n{mensaje}'

        logger.info(f"Attempting to send email to {settings.TARGET_EMAIL}")
        
        send_mail(
            asunto,
            mensaje_correo,
            settings.DEFAULT_FROM_EMAIL,
            [settings.TARGET_EMAIL],
            fail_silently=False,
        )
        
        logger.info("Email sent successfully")
        return JsonResponse({'mensaje': 'Correo enviado exitosamente'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'No se pudo enviar el correo',
            'detalles': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)