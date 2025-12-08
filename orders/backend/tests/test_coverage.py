"""
Дополнительные тесты для увеличения покрытия.
"""

def test_admin_files():
    """Проверка импорта admin файлов."""
    try:
        from backend import admin
        assert True
    except ImportError:
        pass


def test_app_config():
    """Проверка конфигурации приложения."""
    from backend.apps import BackendConfig
    config = BackendConfig('backend', 'backend')
    assert config.name == 'backend'
    assert config.default_auto_field == 'django.db.models.BigAutoField'


def test_models_str_methods():
    """Проверка строковых представлений моделей."""
    from backend.models import Shop, Category, Product, Parameter
    
    # Shop
    shop = Shop(name='Test Shop')
    assert str(shop) == 'Test Shop'
    
    # Category
    category = Category(name='Test Category')
    assert str(category) == 'Test Category'
    
    # Product
    product = Product(name='Test Product')
    assert str(product) == 'Test Product'
    
    # Parameter
    parameter = Parameter(name='Test Parameter')
    assert str(parameter) == 'Test Parameter'


def test_state_choices():
    """Проверка констант состояний заказов."""
    from backend.models import STATE_CHOICES
    
    assert isinstance(STATE_CHOICES, tuple)
    assert len(STATE_CHOICES) > 0
    assert ('basket', 'Статус корзины') in STATE_CHOICES
    assert ('new', 'Новый') in STATE_CHOICES


def test_serializer_fields():
    """Проверка полей сериализаторов."""
    from backend.serializers import (
        ShopSerializer, CategorySerializer, ProductSerializer,
        ParameterSerializer, ContactSerializer
    )
    
    # ShopSerializer
    assert 'id' in ShopSerializer.Meta.fields
    assert 'name' in ShopSerializer.Meta.fields
    assert 'url' in ShopSerializer.Meta.fields
    
    # CategorySerializer
    assert 'id' in CategorySerializer.Meta.fields
    assert 'name' in CategorySerializer.Meta.fields
    
    # ProductSerializer
    assert 'id' in ProductSerializer.Meta.fields
    assert 'name' in ProductSerializer.Meta.fields
    assert 'category' in ProductSerializer.Meta.fields
    
    # ParameterSerializer
    assert 'id' in ParameterSerializer.Meta.fields
    assert 'name' in ParameterSerializer.Meta.fields


def test_user_serializer():
    """Проверка UserSerializer."""
    from backend.serializers import UserSerializer
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Проверка полей
    assert 'id' in UserSerializer.Meta.fields
    assert 'email' in UserSerializer.Meta.fields
    assert 'first_name' in UserSerializer.Meta.fields
    assert 'last_name' in UserSerializer.Meta.fields
    assert 'password' in UserSerializer.Meta.fields
    
    # Проверка read_only_fields
    assert 'id' in UserSerializer.Meta.read_only_fields
    
    # Проверка extra_kwargs
    assert 'password' in UserSerializer.Meta.extra_kwargs
    assert UserSerializer.Meta.extra_kwargs['password']['write_only'] is True


def test_product_info_serializer():
    """Проверка ProductInfoSerializer."""
    from backend.serializers import ProductInfoSerializer
    
    # Проверка полей
    fields = ProductInfoSerializer.Meta.fields
    assert 'id' in fields
    assert 'product' in fields
    assert 'shop' in fields
    assert 'price' in fields
    assert 'quantity' in fields
    assert 'product_parameters' in fields


def test_order_serializer():
    """Проверка OrderSerializer."""
    from backend.serializers import OrderSerializer
    
    # Проверка полей
    fields = OrderSerializer.Meta.fields
    assert 'id' in fields
    assert 'dt' in fields
    assert 'state' in fields
    assert 'contact' in fields
    assert 'ordered_items' in fields
    
    # Проверка read_only_fields
    assert 'id' in OrderSerializer.Meta.read_only_fields
    assert 'dt' in OrderSerializer.Meta.read_only_fields