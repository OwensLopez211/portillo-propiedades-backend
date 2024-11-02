from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso público
def send_email(request):
    data = request.data
    try:
        send_mail(
            subject=data.get('subject', 'Consulta de Usuario'),
            message=f"Nombre: {data['name']}\nTeléfono: {data['phone']}\n\n{data['message']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.TARGET_EMAIL],
        )
        return JsonResponse({'message': 'Correo enviado exitosamente'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)