"""
Сериализаторы для работы с изображениями.
"""

from rest_framework import serializers
from .models import Product, ProductImage
from users.models import User
import os


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для аватара пользователя.
    """
    avatar_url = serializers.SerializerMethodField()
    avatar_thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'avatar', 'avatar_url', 'avatar_thumbnail_url']
        read_only_fields = ['id', 'avatar_url', 'avatar_thumbnail_url']
        extra_kwargs = {
            'avatar': {'write_only': True}
        }
    
    def get_avatar_url(self, obj):
        return obj.avatar_url
    
    def get_avatar_thumbnail_url(self, obj):
        return obj.avatar_thumbnail_url
    
    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        
        if avatar:
            # Удаляем старый аватар
            if instance.avatar:
                if os.path.isfile(instance.avatar.path):
                    os.remove(instance.avatar.path)
            
            # Сохраняем новый
            instance.avatar = avatar
        
        instance.save()
        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для дополнительных изображений товара.
    """
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'thumbnail_url', 'order', 'created_at']
        read_only_fields = ['id', 'image_url', 'thumbnail_url', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.image and hasattr(obj.thumbnail, 'url'):
            return obj.thumbnail.url
        return None


class ProductWithImagesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товара с изображениями.
    """
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'image', 'image_url', 
            'thumbnail_url', 'additional_images'
        ]
        read_only_fields = ['id', 'image_url', 'thumbnail_url']
    
    def get_image_url(self, obj):
        return obj.image_url
    
    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url


class ImageUploadSerializer(serializers.Serializer):
    """
    Сериализатор для загрузки изображений.
    """
    image = serializers.ImageField(
        max_length=255,
        allow_empty_file=False,
        use_url=True
    )
    
    class Meta:
        fields = ['image']