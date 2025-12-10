"""
API endpoints для мониторинга и управления кэшем.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.db import connection
import time

class CacheStatsView(APIView):
    """
    API endpoint для получения статистики кэширования.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Возвращает статистику кэша и производительности.
        """
        try:
            cache_info = {}
            test_results = self._run_performance_tests()
            endpoint_stats = self._get_endpoint_stats()

            cachalot_stats = {
                'enabled': getattr(cache, '_cachalot_enabled', True),
                'cache_alias': getattr(cache, '_cachalot_cache', 'default'),
            }

            return Response({
                'status': True,
                'cache_info': cache_info,
                'performance_tests': test_results,
                'endpoint_stats': endpoint_stats,
                'cachalot_stats': cachalot_stats,
                'timestamp': time.time(),
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def _run_performance_tests(self):
        """
        Запускает тесты производительности с кэшем и без.
        """
        from backend.models import Product, Shop, Category
        import time

        tests = []

        # Тест 1: Получение списка товаров (должно кэшироваться)
        start = time.time()
        products = list(Product.objects.all()[:10])
        db_time = time.time() - start

        start = time.time()
        products_cached = list(Product.objects.all()[:10])
        cached_time = time.time() - start

        tests.append({
            'test': 'product_list_10',
            'database_time': f'{db_time:.4f}s',
            'cached_time': f'{cached_time:.4f}s',
            'improvement': f'{((db_time - cached_time) / db_time * 100):.1f}%',
        })

        # Тест 2: Сложный запрос с join
        from django.db.models import Prefetch
        start = time.time()
        shops_with_products = list(Shop.objects.prefetch_related(
            Prefetch('product_infos__product')
        )[:5])
        db_time = time.time() - start

        start = time.time()
        shops_with_products_cached = list(Shop.objects.prefetch_related(
            Prefetch('product_infos__product')
        )[:5])
        cached_time = time.time() - start

        tests.append({
            'test': 'shops_with_products',
            'database_time': f'{db_time:.4f}s',
            'cached_time': f'{cached_time:.4f}s',
            'improvement': f'{((db_time - cached_time) / db_time * 100):.1f}%',
        })

        return tests
    
    def _get_endpoint_stats(self):
        """
        Получает статистику по endpoint из кэша.
        """
        import re

        endpoint_stats = []
        pattern = re.compile(r'^request_metrics:')

        test_paths = [
            '/api/products',
            '/api/user/contact',
            '/api/orders',
        ]

        for path in test_paths:
            import hashlib
            cache_key = f'reqiest_metrics:{hashlib.md5(path.encode()).hexdigest()}'
            metrics = cache.get(cache_key)
            if metrics:
                endpoint_stats.append(metrics)

        return endpoint_stats
    
class CacheManagementView(APIView):
    """
    API endpoint для управления кэшем.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        Очищает кэш или его часть.
        """
        action = request.data.get('action', '')

        if action == 'clear_all':
            cache.clear()
            return Response({'status': True, 'message': 'Весь кэш очищен'})
        
        elif action == 'clear_products':
            from django.core.cache import caches
            redis_cache = caches['default']

            keys_to_delete = []
            for key in cache._cache.get_client().keys('*products'):
                keys_to_delete.append(key)
            for key in cache._cache.get_client().keys('*cachalot*backend_product*'):
                keys_to_delete.append(key)

            if keys_to_delete:
                cache._cache.get_client().delete(*keys_to_delete)

            return Response({'status': True, 'message': f'Кэш товаров очищен ({len(keys_to_delete)} ключей)'})
        
        elif action == 'clear_orders':
            return Response({'status': True, 'message': 'Кэш заказов очищен'})
        
        elif action == 'disable_cachalot':
            from django.conf import settings
            settings.CACHALOT_ENABLED = False
            return Response({'status': True, 'message': 'Cachalot отключен'})
        
        elif action == 'enable_cachalot':
            from django.conf import settings
            settings.CACHALOT_ENABLED = True
            return Response({'status': True, 'message': 'Cachalot включен'})
        
        else:
            return Response({
                'status': False,
                'error': 'Неизвестное действие',
                'available_actions': ['clear_all', 'clear_products', 'clear_orders', 'disable_cachalot', 'enable_cachalot']
            }, status=status.HTTP_400_BAD_REQUEST)

        