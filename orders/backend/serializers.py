"""
Сериализаторы для моделей приложения.

Содержит сериализаторы для всех моделей, используемых в API.
"""

from rest_framework import serializers

from backend.serializers_images import ProductWithImagesSerializer
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem
from users.models import User


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Shop (Магазин)."""

    class Meta:
        model = Shop
        fields = ['id', 'name', 'url']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category (Категория)."""

    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product (Продукт)."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'category']


class ParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Parameter (Параметр)."""

    class Meta:
        model = Parameter
        fields = ['id', 'name']


class ProductParameterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ProductParameter (Параметр продукта)."""

    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductInfo (Информация о продукте).
    
    Включает вложенные сериализаторы для продукта и его параметров.
    """

    product = ProductWithImagesSerializer()
    product_parameters = ProductParameterSerializer(many=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'model', 'external_id',
                  'quantity', 'price', 'price_rrc', 'product_parameters']
        
class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Contact (Контакт пользователя)."""

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User (Пользователь).
    
    Включает контакты пользователя. Пароль доступен только для записи.
    """

    contacts = ContactSerializer(read_only=True, many=True)
    avatar_url = serializers.SerializerMethodField()
    avatar_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts', 'avatar', 'avatar_url', 
                  'avatar_thumbnail_url', 'password']
        read_only_fields = ['id', 'avatar_url', 'avatar_thumbnail_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'write_only': True}
        }

    def get_avatar_url(self, obj):
        return obj.avatar_url
    
    def get_avatar_thumbnail_url(self, obj):
        return obj.avatar_thumbnail_url

    def create(self, validated_data):
        """
        Создает нового пользователя с хешированием пароля.
        
        Args:
            validated_data: Валидированные данные пользователя
            
        Returns:
            User: Созданный пользователь
        """

        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem (Позиция заказа)."""

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']
        read_only_fields = ['id']

class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order (Заказ)."""
    
    ordered_items = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['id', 'dt', 'state', 'contact', 'ordered_items']
        read_only_fields = ['id', 'dt']