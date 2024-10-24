from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decouple import config
import requests
import json

@csrf_exempt
def get_token(request):
    if request.method == 'POST':
        try:
            # Cargar el cuerpo de la solicitud como JSON
            data = json.loads(request.body)
            code = data.get('code')  # El código de autorización enviado desde el frontend
            code_verifier = data.get('code_verifier')  # El code_verifier enviado desde el frontend
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        if not code or not code_verifier:
            return JsonResponse({'error': 'Missing code or code_verifier'}, status=400)

        # Intercambiar el código por un token de acceso
        response = requests.post(
            'https://api.mercadolibre.com/oauth/token',
            headers={'Content-type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'authorization_code',
                'client_id': config('MERCADOLIBRE_CLIENT_ID'),
                'client_secret': config('MERCADOLIBRE_CLIENT_SECRET'),
                'code': code,
                'redirect_uri': config('MERCADOLIBRE_REDIRECT_URI'),
                'code_verifier': code_verifier,
            }
        )
        print('Client ID:', config('MERCADOLIBRE_CLIENT_ID'))
        print('Client Secret:', config('MERCADOLIBRE_CLIENT_SECRET'))

        token_data = response.json()

        if response.status_code == 200:
            return JsonResponse({'access_token': token_data['access_token']})
        else:
            return JsonResponse({'error': token_data}, status=response.status_code)

    # Manejar las solicitudes GET o cualquier otro método no permitido
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt  # Desactiva la protección CSRF si es necesario
def unlink_mercadolibre(request):
    if request.method == 'POST':
        # Aquí puedes manejar la lógica de desincronización
        # Actualmente no tienes modelos, así que simplemente devolvemos un mensaje de éxito.
        
        # Si en el futuro decides hacer algo como registrar eventos de desincronización o notificar
        # al backend sobre la acción, puedes agregar la lógica aquí.

        return JsonResponse({'message': 'Desincronización exitosa con MercadoLibre'}, status=200)
    
    # Si el método HTTP no es POST, devuelve un error
    return JsonResponse({'error': 'Método no permitido'}, status=405)




#no implementado aun
def refresh_access_token(refresh_token):
    response = requests.post(
        'https://api.mercadolibre.com/oauth/token',
        data={
            'grant_type': 'refresh_token',
            'client_id': config('MERCADOLIBRE_CLIENT_ID'),
            'client_secret': config('MERCADOLIBRE_CLIENT_SECRET'),
            'refresh_token': refresh_token,
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        return token_data  # Devolver los nuevos tokens (access_token y refresh_token)
    else:
        return None  # Manejar el error si es necesario