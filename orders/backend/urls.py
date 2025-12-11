"""
URL конфигурация для API приложения backend.

Определяет все endpoints API и их соответствие views.
"""

from django.urls import path

from backend.views_cache import CacheManagementView, CacheStatsView
from backend.views_images import AdditionalImageDetailView, AdditionalImageListView, ImageCleanupView, ProductImageUploadView, ThumbnailGenerationView, UserAvatarUploadView
from .views import (APIRootView, BasketDetailView, BasketView, ContactDetailView, ContactListView,
OrderConfirmView, OrderDetailView, OrderListView, PartnerUpdate, RegisterView, LoginView, ProductListView)

from .views_social import SocialAuthCallbackView, SocialAuthLoginView, SocialAuthErrorView

from .views_rollbar import (
    RollbarTestView,
    RollbarUnhandledExceptionView,
    RollbarHandledExceptionView,
    RollbarLogTestView,
    RollbarCustomMessageView,
    RollbarDivideByZeroView,
    RollbarKeyErrorView,
    RollbarAttributeErrorView,
    RollbarCeleryTestView,
)

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

    # Endpoints для тестирования Rollbar
    path('rollbar/test', RollbarTestView.as_view(), name='rollbar-test'),
    path('rollbar/test/unhandled', RollbarUnhandledExceptionView.as_view(), name='rollbar-unhandled'),
    path('rollbar/test/handled', RollbarHandledExceptionView.as_view(), name='rollbar-handled'),
    path('rollbar/test/log/<str:level>', RollbarLogTestView.as_view(), name='rollbar-log'),
    path('rollbar/test/custom', RollbarCustomMessageView.as_view(), name='rollbar-custom'),
    path('rollbar/test/zero', RollbarDivideByZeroView.as_view(), name='rollbar-zero'),
    path('rollbar/test/keyerror', RollbarKeyErrorView.as_view(), name='rollbar-keyerror'),
    path('rollbar/test/attribute', RollbarAttributeErrorView.as_view(), name='rollbar-attribute'),
    path('rollbar/test/celery', RollbarCeleryTestView.as_view(), name='rollbar-celery'),

    # Endpoints для работы с изображениями
    path('user/avatar', UserAvatarUploadView.as_view(), name='user-avatar'),
    path('products/<int:product_id>/image', ProductImageUploadView.as_view(), name='product-image-upload'),
    path('products/<int:product_id>/images', AdditionalImageListView.as_view(), name='additional-images-list'),
    path('products/<int:product_id>/images/<int:pk>', AdditionalImageDetailView.as_view(), name='additional-image-detail'),
    
    # Административные endpoints
    path('images/cleanup', ImageCleanupView.as_view(), name='images-cleanup'),
    path('images/generate-thumbnails', ThumbnailGenerationView.as_view(), name='generate-thumbnails'),

    # Endpoints для загрузки/удаления
    path('user/avatar', UserAvatarUploadView.as_view(), name='user-avatar'),
]

