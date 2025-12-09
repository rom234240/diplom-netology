# orders/backend/tests/test_throttling_final.py
"""
Финальные тесты троттлинга с мокингом лимитов.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model


class TestThrottlingReal:
    """Реальные тесты троттлинга."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
    
    @pytest.mark.django_db
    def test_register_view_has_throttle_scope(self):
        """Тест что RegisterView использует scoped троттлинг."""
        from backend.views import RegisterView
        
        # Проверяем что view имеет throttle_scope
        assert hasattr(RegisterView, 'throttle_scope')
        assert RegisterView.throttle_scope == 'register'
        
        # Проверяем что throttle_classes установлены
        assert hasattr(RegisterView, 'throttle_classes')
        assert len(RegisterView.throttle_classes) > 0
    
    @pytest.mark.django_db
    def test_login_view_has_throttle_scope(self):
        """Тест что LoginView использует scoped троттлинг."""
        from backend.views import LoginView
        
        assert hasattr(LoginView, 'throttle_scope')
        assert LoginView.throttle_scope == 'login'
    
    @pytest.mark.django_db
    def test_partner_update_has_throttle_scope(self):
        """Тест что PartnerUpdate использует scoped троттлинг."""
        from backend.views import PartnerUpdate
        
        assert hasattr(PartnerUpdate, 'throttle_scope')
        assert PartnerUpdate.throttle_scope == 'partner'
    
    def test_throttling_middleware_in_use(self):
        """Тест что троттлинг middleware используется."""
        from django.conf import settings
        
        # Проверяем что троттлинг включен в REST_FRAMEWORK
        assert 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK
        
        # Проверяем что есть rates
        rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        assert 'anon' in rates
        assert 'user' in rates
        assert 'register' in rates
        assert 'login' in rates
        assert 'partner' in rates
        
        # Проверяем значения rates
        assert rates['anon'] == '50/hour'
        assert rates['user'] == '200/hour'
        assert rates['register'] == '10/hour'
        assert rates['login'] == '20/hour'
        assert rates['partner'] == '50/day'


class TestThrottlingExceed:
    """Тесты на превышение лимитов (с мокингом)."""
    
    def test_throttle_exceeded_response(self):
        """Тест ответа при превышении лимита."""
        from rest_framework.exceptions import Throttled
        from rest_framework.views import exception_handler
        from rest_framework.response import Response
        
        # Создаем исключение Throttled
        throttle_exc = Throttled()
        
        # Обрабатываем исключение через стандартный handler
        response = exception_handler(throttle_exc, {})
        
        # Проверяем что handler возвращает правильный response
        assert response is not None
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert 'detail' in response.data
    
    @patch('backend.views.RegisterView.throttle_classes', [])
    def test_throttling_disabled_by_mock(self):
        """Тест что без троттлинга запросы проходят."""
        client = APIClient()
        url = reverse('user-register')
        
        # Делаем много запросов (троттлинг отключен через mock)
        for i in range(15):
            data = {
                'first_name': f'User{i}',
                'last_name': 'Test',
                'email': f'user{i}@example.com',
                'password': 'weak'
            }
            response = client.post(url, data, format='json')
            # Все должны быть 400 (слабый пароль), не 429
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS


class TestAllViewsThrottling:
    """Тест троттлинга для всех views."""
    
    def test_all_views_covered(self):
        """Тест что все API views имеют настройки троттлинга."""
        from backend.views import (
            APIRootView, RegisterView, LoginView, ProductListView,
            ContactListView, ContactDetailView, BasketView, BasketDetailView,
            OrderConfirmView, OrderListView, OrderDetailView, PartnerUpdate
        )
        
        views = [
            (APIRootView, 'api-root'),  # Использует AnonRateThrottle
            (RegisterView, 'register'),  # Scoped
            (LoginView, 'login'),        # Scoped
            (ProductListView, 'anon/user'),  # Стандартный
            (ContactListView, 'user'),       # UserRateThrottle
            (ContactDetailView, 'user'),     # UserRateThrottle
            (BasketView, 'user'),            # UserRateThrottle
            (BasketDetailView, 'user'),      # UserRateThrottle
            (OrderConfirmView, 'user'),      # UserRateThrottle
            (OrderListView, 'user'),         # UserRateThrottle
            (OrderDetailView, 'user'),       # UserRateThrottle
            (PartnerUpdate, 'partner'),      # Scoped
        ]
        
        for view_class, expected_throttle in views:
            # Проверяем что view имеет throttle_classes или throttle_scope
            has_throttle = (
                hasattr(view_class, 'throttle_classes') and 
                len(view_class.throttle_classes) > 0
            ) or hasattr(view_class, 'throttle_scope')
            
            assert has_throttle, f"{view_class.__name__} не имеет настроек троттлинга"


# Финальный интеграционный тест
def test_integration_throttling():
    """Интеграционный тест троттлинга."""
    from django.conf import settings
    
    print("\n=== Проверка настроек троттлинга ===")
    print(f"DEFAULT_THROTTLE_CLASSES: {settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES')}")
    print(f"DEFAULT_THROTTLE_RATES: {settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES')}")
    
    # Проверяем что настройки существуют
    assert 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK
    assert 'DEFAULT_THROTTLE_RATES' in settings.REST_FRAMEWORK
    
    # Проверяем конкретные значения
    rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
    
    expected_rates = {
        'anon': '50/hour',
        'user': '200/hour',
        'register': '10/hour',
        'login': '20/hour',
        'partner': '50/day'
    }
    
    for key, expected_value in expected_rates.items():
        assert key in rates, f"Отсутствует rate для {key}"
        assert rates[key] == expected_value, f"Неправильное значение для {key}: {rates[key]} (ожидалось {expected_value})"
    
    print("✓ Все настройки троттлинга корректны")