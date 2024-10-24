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
