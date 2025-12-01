from django.urls import path
from requests import Response
from .views import BasketDetailView, BasketView, ContactDetailView, ContactListView, OrderConfirmView, OrderDetailView, OrderListView, PartnerUpdate, RegisterView, LoginView, ProductListView
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Orders API',
        'endpoints': {
            'register': '/api/user/register',
            'login': '/api/user/login',
            'products': '/api/products',
            'partner_update': '/api/partner/update',
            'basket': '/api/basket',
            'orders': '/api/orders',
            'contacts': '/api/user/contact',
        }
    })

urlpatterns = [
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register', RegisterView.as_view(), name='user-register'),
    path('user/login', LoginView.as_view(), name='user-login'),
    path('products', ProductListView.as_view(), name='product-list'),
    path('user/contact', ContactListView.as_view(), name='contact-list'),
    path('user/contact/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),
    path('basket', BasketView.as_view(), name='basket'),
    path('basket/<int:pk>', BasketDetailView.as_view(), name='basket-detail'),
    path('order/confirm', OrderConfirmView.as_view(), name='order-confirm'),
    path('orders', OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
]