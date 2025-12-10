"""
URL конфигурация для API приложения backend.

Определяет все endpoints API и их соответствие views.
"""

from django.urls import path

from backend.views_cache import CacheManagementView, CacheStatsView
from .views import (APIRootView, BasketDetailView, BasketView, ContactDetailView, ContactListView,
OrderConfirmView, OrderDetailView, OrderListView, PartnerUpdate, RegisterView, LoginView, ProductListView)

from .views_social import SocialAuthCallbackView, SocialAuthLoginView, SocialAuthErrorView

urlpatterns = [
    # Корневой endpoint API
    path('', APIRootView.as_view(), name='api-root'),
    
    # Endpoints для партнеров
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),

    # Endpoints для пользователей
    path('user/register', RegisterView.as_view(), name='user-register'),
    path('user/login', LoginView.as_view(), name='user-login'),
    path('user/contact', ContactListView.as_view(), name='contact-list'),
    path('user/contact/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),

    # Endpoints для товаров
    path('products', ProductListView.as_view(), name='product-list'),

    # Endpoints для корзины
    path('basket', BasketView.as_view(), name='basket'),
    path('basket/<int:pk>', BasketDetailView.as_view(), name='basket-detail'),

    # Endpoints для заказов
    path('order/confirm', OrderConfirmView.as_view(), name='order-confirm'),
    path('orders', OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),

    # Endpoints для социальной авторизации
    path('social/vk/auth', SocialAuthLoginView.as_view(), name='social-vk-auth'),
    path('social/callback', SocialAuthCallbackView.as_view(), name='social-callback'),
    path('social/error', SocialAuthErrorView.as_view(), name='social-error'),

    # Endpoints для кэширования
    path('cache/stats', CacheStatsView.as_view(), name='cache-stats'),
    path('cache/manage', CacheManagementView.as_view(), name='cache-manage'),
]