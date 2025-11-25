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
from .serializers import ContactSerializer, OrderItemSerializer, ProductInfoSerializer, ShopSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q


class PartnerUpdate(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
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
                            price_rss=item['price_rss'],
                            quantity=item['quntity'],
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
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
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
            user.save()
            return Response({'Status': True}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password']
            )

            if user is not None:
                if user.is_active:
                    return Response({'Status': True}, status=status.HTTP_200_OK)
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
    serializer_class = ProductInfoSerializer

    def get_queryset(self):
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
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)
    
class BasketView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order, _ = Order.objects.get_or_create(
            user=self.request.user,
            state='basket'
        )
        return OrderItem.objects.filter(order=order)
    
    def create(self, request, *args, **kwargs):
        if not {'product_info_id', 'quantity'}.issubset(request.data):
            return Response(
                {'Status': False, 'Error': 'Не указаны все необходимые аргументы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order, _ = Order.objects.get_or_create(user=request.user, state='basket')
        
        order_item, created = OrderItem.objects.update_or_create(
            order=order,
            product_info_id=request.data['product_info_id'],
            defaults={'quantity': request.data['quantity']}
        )
        
        serializer = self.get_serializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BasketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        order = Order.objects.filter(user=self.request.user, state='basket').first()
        if order:
            return OrderItem.objects.filter(order=order)
        return OrderItem.objects.none()