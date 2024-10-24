from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

@csrf_exempt
def get_token(request):
    if request.method == 'POST':
        code = request.POST.get('code')  # El código de autorización enviado desde el frontend
        code_verifier = request.POST.get('code_verifier')  # El code_verifier enviado desde el frontend

        if not code or not code_verifier:
            return JsonResponse({'error': 'Missing code or code_verifier'}, status=400)

        # Intercambiar el código por un token de acceso
        response = requests.post(
            'https://api.mercadolibre.com/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': 'YOUR_CLIENT_ID',
                'client_secret': 'YOUR_CLIENT_SECRET',
                'code': code,
                'redirect_uri': 'https://portillo-propiedades-frontend.vercel.app/callback',  # Debe coincidir con la redirect_uri
                'code_verifier': code_verifier,
            }
        )

        token_data = response.json()

        if response.status_code == 200:
            return JsonResponse({'access_token': token_data['access_token']})
        else:
            return JsonResponse({'error': token_data}, status=response.status_code)

    # Manejar las solicitudes GET o cualquier otro método no permitido
    return JsonResponse({'error': 'Invalid request method'}, status=405)
