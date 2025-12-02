"""
Представления (views) для API приложения.

Содержит все API endpoints для работы с магазином, пользователями,
товарами, корзиной и заказами.
"""

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.http import JsonResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from yaml import load as load_yaml, Loader

from users.models import User
from .models import Contact, Order, OrderItem, Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from .serializers import ContactSerializer, OrderItemSerializer, OrderSerializer, ProductInfoSerializer, ShopSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.db import transaction
from rest_framework.authtoken.models import Token
from .emails import send_order_confirmation_email, send_registration_email


class PartnerUpdate(APIView):
    """
    API endpoint для партнеров по обновлению товаров из YAML файла.
    
    Требуется аутентификация партнера.
    """

    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Загружает товары из YAML файла по указанному URL.
        
        Args:
            request: Запрос с данными, содержащими URL YAML файла
            
        Returns:
            JsonResponse: Результат операции импорта
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                try:
                    stream = get(url).content
                    data = load_yaml(stream, Loader=Loader)
                    shop, _ = Shop.objects.get_or_create(name=data['shop'])
                    for category in data['categories']:
                        category_object, _ = Category.objects.get_or_create(
                            id=category['id'],
                            name=category['name']
                        )
                        category_object.shops.add(shop.id)
                        category_object.save()
                    
                    ProductInfo.objects.filter(shop_id=shop.id).delete()
                    
                    for item in data['goods']:
                        product, _ = Product.objects.get_or_create(
                            name=item['name'],
                            category_id=item['category']
                        )

                        product_info = ProductInfo.objects.create(
                            product_id=product.id,
                            external_id=item['id'],
                            model=item['model'],
                            price=item['price'],
                            price_rrc=item['price_rrc'],
                            quantity=item['quantity'],
                            shop_id=shop.id
                        )

                        for name, value in item['parameters'].items():
                            parameter_object, _ = Parameter.objects.get_or_create(name=name)
                            ProductParameter.objects.create(
                                product_info_id=product_info.id,
                                parameter_id=parameter_object.id,
                                value=value
                            )
                    
                    return JsonResponse({'Status': True})
                
                except Exception as e:
                    return JsonResponse({'Status': False, 'Error': str(e)})
        
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    
class RegisterView(APIView):
    """
    API endpoint для регистрации новых пользователей.
    """
     
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Регистрирует нового пользователя.
        
        Args:
            request: Запрос с данными пользователя
            
        Returns:
            Response: Результат регистрации
        """
        if not all([request.data.get('first_name'), 
                   request.data.get('last_name'), 
                   request.data.get('email'), 
                   request.data.get('password')]):
            return Response(
                {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(request.data['password'])
        except ValidationError as e:
            return Response(
                {'Status': False, 'Error': ', '.join(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {'Status': False, 'Error': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            try:
                send_registration_email(
                    user_email=user.email,
                    user_name=f'{user.first_name} {user.last_name}'
                )
            except Exception as e:
                print(f'Ошибка отправки email: {e}')

            return Response({'Status': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    """
    API endpoint для аутентификации пользователей.
    
    Возвращает токен для доступа к защищенным endpoints.
    """

    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        """
        Аутентифицирует пользователя и возвращает токен.
        
        Args:
            request: Запрос с email и паролем
            
        Returns:
            Response: Токен и информация о пользователе
        """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password']
            )

            if user is not None:
                if user.is_active:
                    token, creared = Token.objects.get_or_create(user=user)
                    return Response({
                        'Status': True,
                        'Token': token.key,
                        'User': {
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                    },status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'Status': False, 'Error': 'Учетная запись не активна'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'Status': False, 'Error': 'Неверный email или пароль'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ProductListView(generics.ListAPIView):
    """
    API endpoint для получения списка товаров.
    
    Поддерживает фильтрацию по категории, магазину и поиск.
    """

    serializer_class = ProductInfoSerializer

    def get_queryset(self):
        """
        Возвращает отфильтрованный queryset товаров.
        
        Returns:
            QuerySet: Отфильтрованный список товаров
        """
        queryset = ProductInfo.objects.filter(
            quantity__gt=0
        ).select_related('product', 'shop', 'product__category').prefetch_related('product_parameters')

        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)

        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) |
                Q(model__icontains=search)
            )
        return queryset
    
class ContactListView(generics.ListCreateAPIView):
    """
    API endpoint для работы с контактами пользователя.
    
    GET: получение списка контактов
    POST: создание нового контакта
    """

    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает контакты текущего пользователя.
        
        Returns:
            QuerySet: Контакты пользователя
        """
        return Contact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Сохраняет контакт с привязкой к текущему пользователю.
        
        Args:
            serializer: Сериализатор контакта
        """
        serializer.save(user=self.request.user)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с конкретным контактом.
    
    GET: получение контакта
    PUT: обновление контакта
    DELETE: удаление контакта
    """

    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает контакты текущего пользователя.
        
        Returns:
            QuerySet: Контакты пользователя
        """
        return Contact.objects.filter(user=self.request.user)
    
class BasketView(generics.ListCreateAPIView):
    """
    API endpoint для работы с корзиной пользователя.
    
    GET: получение содержимого корзины
    POST: добавление товара в корзину
    """

    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает товары в корзине текущего пользователя.
        
        Returns:
            QuerySet: Товары в корзине
        """
        order, _ = Order.objects.get_or_create(
            user=self.request.user,
            state='basket'
        )
        return OrderItem.objects.filter(order=order)
    
    def create(self, request, *args, **kwargs):
        """
        Добавляет товар в корзину или обновляет количество.
        
        Args:
            request: Запрос с ID товара и количеством
            
        Returns:
            Response: Результат операции
        """
        if not {'product_info_id', 'quantity'}.issubset(request.data):
            return Response(
                {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product_info = ProductInfo.objects.get(id=request.data['product_info_id'])
        except ProductInfo.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Товар не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        
        order_item, created = OrderItem.objects.update_or_create(
            order=order,
            product_info=product_info,
            defaults={'quantity': request.data['quantity']}
        )
        
        serializer = self.get_serializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BasketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с конкретным товаром в корзине.
    
    GET: получение информации о товаре в корзине
    PUT: обновление количества товара
    DELETE: удаление товара из корзины
    """

    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает товары в корзине текущего пользователя.
        
        Returns:
            QuerySet: Товары в корзине
        """
        order = Order.objects.filter(user=self.request.user, state='basket').first()
        if order:
            return OrderItem.objects.filter(order=order)
        return OrderItem.objects.none()
    
class OrderConfirmView(APIView):
    """
    API endpoint для подтверждения заказа (оформления корзины).
    
    Переводит заказ из состояния 'basket' в 'new'.
    """
    
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Подтверждает заказ, проверяя наличие товаров и вычитая их количество.
        
        Args:
            request: Запрос с ID контакта для доставки
            
        Returns:
            Response: Результат подтверждения заказа
        """
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response(
                {'Status': False, 'Error': 'Не указан контакт (contact_id)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Контакт не найден или не принадлежит пользователю'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(user=request.user, state='basket')
        except Order.DoesNotExist:
            return Response(
                {'Status': False, 'Error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                for item in order.ordered_items.all():
                    if item.product_info.quantity < item.quantity:
                        return Response(
                            {'Status': False, 'Error': f'Недостаточно товара: {item.product_info.product.name}. Доступно: {item.product_info.quantity}, запрошено: {item.quantity}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    item.product_info.quantity -= item.quantity
                    item.product_info.save()

                order.state ='new'
                order.contact = contact
                order.save()

                try:
                    send_order_confirmation_email(
                    user_email=request.user.email,
                    user_name=f'{request.user.first_name} {request.user.last_name}',
                    order_id=order.id
                    )
                except Exception as e:
                    print(f"Ошибка отправки email: {e}")
                    
                return Response({'Status': True, 'order_id': order.id})
            
        except Exception as e:
            return Response(
                {'Status': False, 'Error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class OrderListView(generics.ListAPIView):
    """
    API endpoint для получения списка заказов пользователя.
    
    Не включает заказы со статусом 'basket' (корзина).
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает заказы текущего пользователя, исключая корзину.
        
        Returns:
            QuerySet: Заказы пользователя
        """
        return Order.objects.filter(
            user=self.request.user
        ).exclude(state='basket').order_by('-dt')
    
class OrderDetailView(generics.RetrieveAPIView):
    """
    API endpoint для получения деталей конкретного заказа.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает заказы текущего пользователя.
        
        Returns:
            QuerySet: Заказы пользователя
        """
        return Order.objects.filter(user=self.request.user)
    
class APIRootView(APIView):
    """
    Корневой endpoint API.
    
    Возвращает информацию о доступных endpoints и инструкции по использованию.
    """

    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Возвращает информацию о всех доступных endpoints API.
        
        Returns:
            Response: JSON с описанием API
        """

        return Response({
            'message': 'Добро пожаловать в API магазина!',
            'endpoints': {
                'partner': {
                    'update': '/api/partner/update',
                    'description': 'Обновление товаров партнера'
                },
                'user': {
                    'register': '/api/user/register',
                    'login': '/api/user/login',
                    'contacts': '/api/user/contact',
                },
                'products': {
                    'list': '/api/products',
                    'description': 'Список товаров с фильтрацией'
                },
                'basket': {
                    'list_create': '/api/basket',
                    'detail': '/api/basket/<id>',
                    'description': 'Работа с корзиной'
                },
                'orders': {
                    'confirm': '/api/order/confirm',
                    'list': '/api/orders',
                    'detail': '/api/order/<id>',
                    'description': 'Работа с заказами'
                }
            },
            'instructions': {
                'authentication': 'Используйте TokenAuthentication. Получите токен через /api/user/login',
                'examples': {
                    'login': 'POST /api/user/login {"email": "...", "password": "..."}',
                    'get_products': 'GET /api/products (требуется токен)',
                    'add_to_basket': 'POST /api/basket {"product_info_id": 1, "quantity": 2}'
                }
            }
        })