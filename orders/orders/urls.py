"""
URL configuration for orders project.

Основной URL-конфигурационный файл Django-проекта.

Определяет маршруты для:
- Административной панели Django
- API endpoints приложения backend
- Документации API (Swagger/ReDoc)
- Домашней страницы

Использует:
- django.contrib.admin: административный интерфейс
- backend.urls: маршруты API приложения backend
- drf_yasg: автоматическая генерация документации OpenAPI/Swagger

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static


# Конфигурация схемы OpenAPI/Swagger для автоматической генерации документации
schema_view = get_schema_view(
    openapi.Info(
        title='Orders API',
        default_version = 'v1',
        description='API для системы заказов',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='contact@orders.local'),
        license=openapi.License(name='BSD License')
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Основные URL-маршруты проекта
urlpatterns = [
    # JET админка (должна быть перед стандартной админкой)
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),

    # Административная панель Django
    path('admin/', admin.site.urls),

    # API endpoints приложения backend (основная бизнес-логика)
    path('api/', include('backend.urls')),

    # Социальная авторизация
     path('auth/', include('social_django.urls', namespace='social')),

    # Документация OpenAPI в формате JSON/YAML (для интеграции)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Интерактивная документация Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Альтернативная документация ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Домашняя страница (перенаправляет на Swagger UI)
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='home'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
