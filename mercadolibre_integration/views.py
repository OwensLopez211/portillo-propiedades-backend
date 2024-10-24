import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Vista para intercambiar el código de autorización por un token de acceso
@csrf_exempt  # Desactiva la verificación CSRF para esta vista
def get_token(request):
    if request.method == 'POST':
        code = request.POST.get('code')  # El código de autorización enviado desde el frontend
        code_verifier = request.POST.get('code_verifier')  # El code_verifier enviado desde el frontend

        # Intercambiar el código por un token de acceso
        response = requests.post(
            'https://api.mercadolibre.com/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': 'YOUR_CLIENT_ID',  # Reemplaza con tu client_id de MercadoLibre
                'client_secret': 'YOUR_CLIENT_SECRET',  # Reemplaza con tu client_secret de MercadoLibre
                'code': code,
                'redirect_uri': 'https://portillo-propiedades-frontend.vercel.app/callback',  # Tu redirect_uri
                'code_verifier': code_verifier,
            }
        )

        token_data = response.json()

        if response.status_code == 200:
            # Devuelve el token de acceso en la respuesta
            return JsonResponse({'access_token': token_data['access_token']})
        else:
            # Si hubo un error, devuelve la respuesta con el error
            return JsonResponse({'error': token_data}, status=response.status_code)
