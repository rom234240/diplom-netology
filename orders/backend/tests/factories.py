import factory
from django.contrib.auth import get_user_model
from backend.models import Shop, Category, Product, ProductInfo, Contact, Order, OrderItem
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания пользователей."""
    
    class Meta:
        model = get_user_model()
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class ShopFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания магазинов."""
    
    class Meta:
        model = Shop
    
    name = factory.Sequence(lambda n: f'Shop {n}')
    url = factory.Faker('url')


class CategoryFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания категорий."""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n}')


class ProductFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания продуктов."""
    
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f'Product {n}')
    category = factory.SubFactory(CategoryFactory)


class ProductInfoFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания информации о продуктах."""
    
    class Meta:
        model = ProductInfo
    
    product = factory.SubFactory(ProductFactory)
    shop = factory.SubFactory(ShopFactory)
    external_id = factory.Sequence(lambda n: n)
    model = factory.Sequence(lambda n: f'Model {n}')
    quantity = 100
    price = 1000
    price_rrc = 1200


class ContactFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания контактов."""
    
    class Meta:
        model = Contact
    
    user = factory.SubFactory(UserFactory)
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    house = factory.Sequence(lambda n: str(n))
    phone = factory.Faker('phone_number')


class OrderFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания заказов."""
    
    class Meta:
        model = Order
    
    user = factory.SubFactory(UserFactory)
    state = 'basket'
    contact = None