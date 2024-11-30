from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from properties.models import Property
from decouple import config
import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

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

@api_view(['GET'])
def get_mercadolibre_items(request):
    access_token = request.user.mercadolibre_access_token  # Asegúrate de obtener el token de acceso de MercadoLibre del usuario

    # Obtén los datos del usuario en MercadoLibre
    user_response = requests.get(
        'https://api.mercadolibre.com/users/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if user_response.status_code != 200:
        return Response({'error': 'Error al obtener los datos del usuario en MercadoLibre'}, status=400)

    user_data = user_response.json()
    user_id = user_data['id']

    # Ahora obtén los ítems (publicaciones) del usuario
    items_response = requests.get(
        f'https://api.mercadolibre.com/users/{user_id}/items/search',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if items_response.status_code != 200:
        return Response({'error': 'Error al obtener las publicaciones'}, status=400)

    items_data = items_response.json()
    return Response(items_data)

@api_view(['GET'])
def sync_mercadolibre_properties(request):
    # Asegúrate de que el usuario tenga un token de acceso a MercadoLibre
    access_token = request.user.mercadolibre_access_token

    # Obtén el `user_id` de MercadoLibre
    user_response = requests.get(
        'https://api.mercadolibre.com/users/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if user_response.status_code != 200:
        return Response({'error': 'Error al obtener los datos del usuario en MercadoLibre'}, status=400)

    user_data = user_response.json()
    user_id = user_data['id']  # Este es el ID del usuario en MercadoLibre

    # Obtener las publicaciones del usuario en MercadoLibre
    items_response = requests.get(
        f'https://api.mercadolibre.com/users/{user_id}/items/search',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if items_response.status_code != 200:
        return Response({'error': 'Error al obtener las publicaciones'}, status=400)

    items_data = items_response.json()

    # Recorre los resultados de las publicaciones
    for item_id in items_data['results']:
        # Para cada publicación, obtén más detalles
        item_response = requests.get(
            f'https://api.mercadolibre.com/items/{item_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if item_response.status_code == 200:
            item_data = item_response.json()

            # Guarda o actualiza la propiedad en tu base de datos
            Property.objects.update_or_create(
                mercadolibre_id=item_data['id'],  # Asegúrate de tener este campo en tu modelo
                defaults={
                    'title': item_data['title'],
                    'precio_venta': item_data.get('price', 0),
                    'descripcion': item_data.get('description', {}).get('plain_text', ''),
                    'direccion': item_data.get('location', {}).get('address_line', ''),
                    'latitud': item_data.get('location', {}).get('latitude', None),
                    'longitud': item_data.get('location', {}).get('longitude', None),
                    'publicada': item_data.get('date_created'),
                    'tipo_operacion': item_data.get('buying_mode'),  # Alquiler/venta (verifica si aplica)
                    'created_by': request.user,  # Asigna la propiedad al usuario autenticado en tu plataforma
                }
            )

    return Response({'message': 'Propiedades sincronizadas con éxito'})