"""
Views для работы с изображениями.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Product, ProductImage
from users.models import User
from .serializers_images import (
    AvatarSerializer,
    ProductImageSerializer,
    ProductWithImagesSerializer,
    ImageUploadSerializer
)
from .tasks_images import (
    process_user_avatar,
    process_product_image,
    cleanup_orphaned_images,
    generate_missing_thumbnails
)


class UserAvatarUploadView(APIView):
    """
    API endpoint для загрузки аватара пользователя.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Возвращает информацию об аватаре текущего пользователя.
        """
        user = request.user
        
        return Response({
            'status': True,
            'avatar_url': user.avatar_url,
            'thumbnail_url': user.avatar_thumbnail_url,
            'has_avatar': bool(user.avatar)
        })
    
    def post(self, request, *args, **kwargs):
        """
        Загружает аватар для текущего пользователя.
        """
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Запускаем асинхронную обработку аватара
            process_user_avatar.delay(user.id)
            
            return Response({
                'status': True,
                'message': 'Аватар успешно загружен',
                'avatar_url': user.avatar_url,
                'thumbnail_url': user.avatar_thumbnail_url
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """
        Удаляет аватар пользователя.
        """
        user = request.user
        
        if user.avatar:
            # Удаляем файл
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            
            return Response({
                'status': True,
                'message': 'Аватар удален'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': False,
            'message': 'Аватар не найден'
        }, status=status.HTTP_404_NOT_FOUND)


class ProductImageUploadView(APIView):
    """
    API endpoint для загрузки основного изображения товара.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id, *args, **kwargs):
        """
        Возвращает информацию об основном изображении товара.
        """
        product = get_object_or_404(Product, id=product_id)
        
        return Response({
            'status': True,
            'product_id': product.id,
            'product_name': product.name,
            'image_url': product.image_url,
            'thumbnail_url': product.thumbnail_url,
            'has_image': bool(product.image),
            'additional_images_count': product.additional_images.count()
        })
    
    def post(self, request, product_id, *args, **kwargs):
        """
        Загружает основное изображение для товара.
        """
        product = get_object_or_404(Product, id=product_id)
        
        serializer = ProductWithImagesSerializer(
            product, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Запускаем асинхронную обработку
            process_product_image.delay(product.id)
            
            return Response({
                'status': True,
                'message': 'Изображение товара успешно загружено',
                'image_url': product.image_url,
                'thumbnail_url': product.thumbnail_url
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, product_id, *args, **kwargs):
        """
        Удаляет основное изображение товара.
        """
        product = get_object_or_404(Product, id=product_id)
        
        if product.image:
            # Удаляем файл
            product.image.delete(save=False)
            product.image = None
            product.save()
            
            return Response({
                'status': True,
                'message': 'Изображение товара удалено'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': False,
            'message': 'Изображение товара не найдено'
        }, status=status.HTTP_404_NOT_FOUND)


class AdditionalImageListView(generics.ListCreateAPIView):
    """
    API endpoint для работы с дополнительными изображениями товара.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        return ProductImage.objects.filter(product=product)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(product=product)
        
        # Запускаем обработку нового изображения
        if serializer.instance and serializer.instance.image:
            from .tasks_images import process_additional_image
            process_additional_image.delay(serializer.instance.id)


class AdditionalImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с конкретным дополнительным изображением.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        return ProductImage.objects.filter(product=product)


class ImageCleanupView(APIView):
    """
    API endpoint для запуска очистки изображений.
    Только для администраторов.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """
        Запускает очистку orphaned изображений.
        """
        task = cleanup_orphaned_images.delay()
        
        return Response({
            'status': True,
            'message': 'Очистка изображений запущена',
            'task_id': task.id
        }, status=status.HTTP_200_OK)


class ThumbnailGenerationView(APIView):
    """
    API endpoint для генерации отсутствующих миниатюр.
    Только для администраторов.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """
        Запускает генерацию миниатюр.
        """
        task = generate_missing_thumbnails.delay()
        
        return Response({
            'status': True,
            'message': 'Генерация миниатюр запущена',
            'task_id': task.id
        }, status=status.HTTP_200_OK)