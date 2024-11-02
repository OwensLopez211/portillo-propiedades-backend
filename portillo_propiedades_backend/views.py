from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LogoutView(APIView):
    def post(self, request):
        # Invalida la sesión del usuario
        logout(request)
        return Response({"message": "Sesión cerrada correctamente"}, status=status.HTTP_200_OK)
