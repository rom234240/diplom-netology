import pytest
from django.urls import reverse
from rest_framework import status

from orders.backend.models import OrderItem
from orders.backend.tests.factories import CategoryFactory, ContactFactory, OrderFactory, ProductInfoFactory, ShopFactory, UserFactory


class TestAPIRootView:
    """Тесты для корневого представления API."""
    
    def test_api_root_returns_200(self, api_client):
        """Тест доступности корневого endpoint."""
        url = reverse('api-root')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'endpoints' in response.data
        assert 'message' in response.data
    
    def test_api_root_contains_all_endpoints(self, api_client):
        """Тест что корневой endpoint содержит все необходимые endpoints."""
        url = reverse('api-root')
        response = api_client.get(url)
        
        endpoints = response.data['endpoints']
        
        assert 'partner' in endpoints
        assert 'user' in endpoints
        assert 'products' in endpoints
        assert 'basket' in endpoints
        assert 'orders' in endpoints
        
        # Проверяем ключевые endpoints
        assert 'register' in endpoints['user']
        assert 'login' in endpoints['user']
        assert 'list' in endpoints['products']

class TestProductListView:
    """Тесты для списка товаров."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестовых данных."""
        self.shop = ShopFactory()
        self.category = CategoryFactory()
        self.category.shops.add(self.shop)
        
        # Создаем несколько товаров
        self.product_info1 = ProductInfoFactory(
            shop=self.shop,
            product__category=self.category,
            quantity=10
        )
        self.product_info2 = ProductInfoFactory(
            shop=self.shop,
            product__category=self.category,
            quantity=0  # Нет в наличии
        )
        self.product_info3 = ProductInfoFactory(
            shop=self.shop,
            quantity=5  # Другой магазин
        )
    
    def test_product_list_returns_200(self, api_client):
        """Тест доступности списка товаров."""
        url = reverse('product-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_product_list_only_shows_available_products(self, api_client):
        """Тест что отображаются только товары в наличии."""
        url = reverse('product-list')
        response = api_client.get(url)
        
        # Должны быть только товары с quantity > 0
        assert len(response.data) == 2  # product_info1 и product_info3
    
    def test_product_list_filter_by_category(self, api_client):
        """Тест фильтрации по категории."""
        url = reverse('product-list')
        response = api_client.get(url, {'category_id': self.category.id})
        
        assert len(response.data) == 1
        assert response.data[0]['product']['category'] == self.category.id
    
    def test_product_list_filter_by_shop(self, api_client):
        """Тест фильтрации по магазину."""
        url = reverse('product-list')
        response = api_client.get(url, {'shop_id': self.shop.id})
        
        assert len(response.data) == 1
        assert response.data[0]['shop'] == self.shop.id
    
    def test_product_list_search(self, api_client):
        """Тест поиска товаров."""
        url = reverse('product-list')
        
        # Поиск по названию продукта
        response = api_client.get(url, {'search': self.product_info1.product.name})
        assert len(response.data) >= 1
        
        # Поиск по модели
        response = api_client.get(url, {'search': self.product_info1.model})
        assert len(response.data) >= 1

class TestRegisterView:
    """Тесты для регистрации пользователей."""
    
    def test_register_user_success(self, api_client):
        """Тест успешной регистрации пользователя."""
        url = reverse('user-register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'StrongPass123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['Status'] is True
        assert 'User registered successfully' in str(response.data)
    
    def test_register_user_missing_fields(self, api_client):
        """Тест регистрации с недостающими полями."""
        url = reverse('user-register')
        data = {
            'first_name': 'John',
            'email': 'john@example.com'
            # Нет last_name и password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Не указаны все необходимые аргументы' in response.data['Error']
    
    def test_register_user_weak_password(self, api_client):
        """Тест регистрации со слабым паролем."""
        url = reverse('user-register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': '123'  # Слабый пароль
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'password' in str(response.data['Error']).lower()
    
    def test_register_user_duplicate_email(self, api_client, user):
        """Тест регистрации с уже существующим email."""
        url = reverse('user-register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': user.email,  # Email уже существует
            'password': 'StrongPass123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'уже существует' in response.data['Error']

class TestLoginView:
    """Тесты для аутентификации пользователей."""
    
    def test_login_success(self, api_client, user):
        """Тест успешного входа."""
        url = reverse('user-login')
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['Status'] is True
        assert 'Token' in response.data
        assert 'User' in response.data
        assert response.data['User']['email'] == user.email
    
    def test_login_wrong_password(self, api_client, user):
        """Тест входа с неверным паролем."""
        url = reverse('user-login')
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Неверный email или пароль' in response.data['Error']
    
    def test_login_missing_fields(self, api_client):
        """Тест входа без обязательных полей."""
        url = reverse('user-login')
        data = {
            'email': 'test@example.com'
            # Нет password
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Не указаны все необходимые аргументы' in response.data['Error']
    
    def test_login_nonexistent_user(self, api_client):
        """Тест входа несуществующего пользователя."""
        url = reverse('user-login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Неверный email или пароль' in response.data['Error']

class TestContactListView:
    """Тесты для работы с контактами."""
    
    def test_get_contacts_requires_auth(self, api_client):
        """Тест что получение контактов требует аутентификации."""
        url = reverse('contact-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_contacts_authenticated(self, authenticated_client, user):
        """Тест получения контактов аутентифицированным пользователем."""
        # Создаем контакты для пользователя
        contact1 = ContactFactory(user=user)
        contact2 = ContactFactory(user=user)
        # Контакт другого пользователя
        ContactFactory()
        
        url = reverse('contact-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Только контакты текущего пользователя
    
    def test_create_contact_success(self, authenticated_client, user):
        """Тест успешного создания контакта."""
        url = reverse('contact-list')
        data = {
            'city': 'Москва',
            'street': 'Ленина',
            'house': '10',
            'phone': '+79161234567'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['city'] == 'Москва'
        assert response.data['user'] == user.id
    
    def test_create_contact_invalid_data(self, authenticated_client):
        """Тест создания контакта с невалидными данными."""
        url = reverse('contact-list')
        data = {
            'city': '',  # Пустой город
            'street': 'Ленина',
            'phone': 'invalid_phone'  # Неверный телефон
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestBasketView:
    """Тесты для работы с корзиной."""
    
    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Настройка тестовых данных."""
        self.user = user
        self.product_info = ProductInfoFactory(quantity=10)
    
    def test_get_basket_requires_auth(self, api_client):
        """Тест что получение корзины требует аутентификации."""
        url = reverse('basket')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_empty_basket(self, authenticated_client):
        """Тест получения пустой корзины."""
        url = reverse('basket')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_add_to_basket_success(self, authenticated_client):
        """Тест успешного добавления товара в корзину."""
        url = reverse('basket')
        data = {
            'product_info_id': self.product_info.id,
            'quantity': 2
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['product_info'] == self.product_info.id
        assert response.data['quantity'] == 2
    
    def test_add_to_basket_missing_fields(self, authenticated_client):
        """Тест добавления в корзину без обязательных полей."""
        url = reverse('basket')
        data = {
            'product_info_id': self.product_info.id
            # Нет quantity
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Не указаны все необходимые аргументы' in response.data['Error']
    
    def test_add_to_basket_nonexistent_product(self, authenticated_client):
        """Тест добавления несуществующего товара."""
        url = reverse('basket')
        data = {
            'product_info_id': 99999,  # Несуществующий ID
            'quantity': 2
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Товар не найден' in response.data['Error']
    
    def test_add_to_basket_insufficient_quantity(self, authenticated_client):
        """Тест добавления большего количества, чем есть в наличии."""
        url = reverse('basket')
        data = {
            'product_info_id': self.product_info.id,
            'quantity': 100  # Больше чем есть в наличии (10)
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        # Пока что нет проверки на количество при добавлении в корзину
        # Этот тест проверяет что товар добавляется в любом случае
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_update_basket_item_quantity(self, authenticated_client):
        """Тест обновления количества товара в корзине."""
        # Сначала добавляем товар
        url = reverse('basket')
        data = {
            'product_info_id': self.product_info.id,
            'quantity': 2
        }
        authenticated_client.post(url, data, format='json')
        
        # Обновляем количество
        data['quantity'] = 5
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 5

class TestOrderConfirmView:
    """Тесты для подтверждения заказов."""
    
    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Настройка тестовых данных."""
        self.user = user
        self.product_info = ProductInfoFactory(quantity=10)
        self.contact = ContactFactory(user=user)
        
        # Создаем корзину с товаром
        self.order = OrderFactory(user=user, state='basket')
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_info=self.product_info,
            quantity=2
        )
    
    def test_confirm_order_requires_auth(self, api_client):
        """Тест что подтверждение заказа требует аутентификации."""
        url = reverse('order-confirm')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_confirm_order_success(self, authenticated_client):
        """Тест успешного подтверждения заказа."""
        url = reverse('order-confirm')
        data = {
            'contact_id': self.contact.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['Status'] is True
        assert 'order_id' in response.data
        
        # Проверяем что статус заказа изменился
        self.order.refresh_from_db()
        assert self.order.state == 'new'
        assert self.order.contact == self.contact
    
    def test_confirm_order_missing_contact(self, authenticated_client):
        """Тест подтверждения заказа без контакта."""
        url = reverse('order-confirm')
        data = {}  # Нет contact_id
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Не указан контакт' in response.data['Error']
    
    def test_confirm_order_nonexistent_contact(self, authenticated_client):
        """Тест подтверждения заказа с несуществующим контактом."""
        url = reverse('order-confirm')
        data = {
            'contact_id': 99999  # Несуществующий контакт
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Контакт не найден' in response.data['Error']
    
    def test_confirm_order_insufficient_quantity(self, authenticated_client):
        """Тест подтверждения заказа с недостаточным количеством товара."""
        # Устанавливаем большое количество в корзине
        self.order_item.quantity = 100
        self.order_item.save()
        
        url = reverse('order-confirm')
        data = {
            'contact_id': self.contact.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Недостаточно товара' in response.data['Error']
    
    def test_confirm_order_empty_basket(self, authenticated_client, user):
        """Тест подтверждения пустой корзины."""
        # Создаем пользователя без корзины
        new_user = UserFactory()
        authenticated_client.force_authenticate(user=new_user)
        
        url = reverse('order-confirm')
        data = {
            'contact_id': self.contact.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['Status'] is False
        assert 'Корзина пуста' in response.data['Error']

class TestOrderListView:
    """Тесты для списка заказов."""
    
    @pytest.fixture(autouse=True)
    def setup(self, user):
        """Настройка тестовых данных."""
        self.user = user
        
        # Создаем заказы разных статусов
        self.order1 = OrderFactory(user=user, state='new')
        self.order2 = OrderFactory(user=user, state='confirmed')
        self.order3 = OrderFactory(user=user, state='delivered')
        self.basket = OrderFactory(user=user, state='basket')  # Корзина
    
    def test_get_orders_requires_auth(self, api_client):
        """Тест что получение заказов требует аутентификации."""
        url = reverse('order-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_orders_excludes_basket(self, authenticated_client):
        """Тест что список заказов не включает корзину."""
        url = reverse('order-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # Только заказы, не корзина
    
    def test_get_orders_only_current_user(self, authenticated_client, user):
        """Тест что пользователь видит только свои заказы."""
        # Создаем заказ другого пользователя
        other_user = UserFactory()
        OrderFactory(user=other_user, state='new')
        
        url = reverse('order-list')
        response = authenticated_client.get(url)
        
        assert len(response.data) == 3  # Только заказы текущего пользователя
    
    def test_orders_sorted_by_date_desc(self, authenticated_client):
        """Тест что заказы отсортированы по дате (новые первыми)."""
        url = reverse('order-list')
        response = authenticated_client.get(url)
        
        dates = [order['dt'] for order in response.data]
        assert dates == sorted(dates, reverse=True)

class TestPartnerUpdate:
    """Тесты для обновления товаров партнера."""
    
    @pytest.fixture
    def yaml_content(self):
        """Фикстура с тестовым YAML контентом."""
        return """
shop: Test Shop
categories:
  - id: 1
    name: Электроника
  - id: 2
    name: Одежда
goods:
  - id: 123
    category: 1
    name: Смартфон
    model: Model X
    price: 10000
    price_rrc: 12000
    quantity: 10
    parameters:
      color: Черный
      memory: 128GB
  - id: 456
    category: 2
    name: Футболка
    model: Basic
    price: 500
    price_rrc: 700
    quantity: 50
    parameters:
      size: L
      material: Хлопок
"""
    
    def test_partner_update_requires_auth(self, api_client):
        """Тест что обновление товаров требует аутентификации."""
        url = reverse('partner-update')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Log in required' in response.data['Error']
    
    def test_partner_update_missing_url(self, authenticated_client):
        """Тест обновления без URL."""
        url = reverse('partner-update')
        response = authenticated_client.post(url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Не указаны все необходимые аргументы' in response.data['Errors']
    
    def test_partner_update_invalid_url(self, authenticated_client):
        """Тест обновления с невалидным URL."""
        url = reverse('partner-update')
        data = {'url': 'invalid-url'}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Error' in response.data