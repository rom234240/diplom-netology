import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def factory():
    """Фикстура для RequestFactory."""
    return RequestFactory()


@pytest.fixture
def user():
    """Фикстура для создания пользователя."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Фикстура для создания администратора."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Фикстура для аутентифицированного клиента."""
    api_client.force_authenticate(user=user)
    return api_client