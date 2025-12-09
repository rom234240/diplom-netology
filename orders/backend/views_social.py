"""
Views для социальной авторизации через VK.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token


class SocialAuthCallbackView(APIView):
    """
    API endpoint для обработки callback от социальной авторизации.
    После успешной авторизации через VK пользователь будет перенаправлен сюда.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET запрос после успешной социальной авторизации.
        
        Returns:
            Response: JSON с токеном и информацией о пользователе или URL для авторизации
        """
        if request.user.is_authenticated:
            # Пользователь уже аутентифицирован через социальную сеть
            token, created = Token.objects.get_or_create(user=request.user)
            
            return Response({
                'status': True,
                'message': 'Успешная авторизация через VK',
                'token': token.key,
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                }
            }, status=status.HTTP_200_OK)
        else:
            # Пользователь не аутентифицирован, возможно нужно начать процесс
            return Response({
                'status': False,
                'error': 'Пользователь не аутентифицирован',
                'auth_url': '/auth/login/vk-oauth2/'
            }, status=status.HTTP_401_UNAUTHORIZED)


class SocialAuthLoginView(APIView):
    """
    API endpoint для получения ссылки на авторизацию через VK.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Возвращает URL для авторизации через VK.
        
        Returns:
            Response: JSON с URL для авторизации
        """
        from django.urls import reverse
        
        vk_auth_url = reverse('social:begin', args=['vk-oauth2'])
        full_url = request.build_absolute_uri(vk_auth_url)
        
        return Response({
            'status': True,
            'auth_url': full_url,
            'method': 'GET',
            'instructions': 'Перейдите по этой ссылке для авторизации через VK'
        })


class SocialAuthErrorView(APIView):
    """
    API endpoint для обработки ошибок социальной авторизации.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Обрабатывает ошибки социальной авторизации.
        
        Returns:
            Response: JSON с описанием ошибки
        """
        error_message = request.GET.get('message', 'Неизвестная ошибка авторизации')
        
        return Response({
            'status': False,
            'error': 'Ошибка авторизации через VK',
            'message': error_message,
            'retry_url': '/api/social/vk/auth'
        }, status=status.HTTP_400_BAD_REQUEST)