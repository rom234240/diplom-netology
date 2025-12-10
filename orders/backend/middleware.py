"""
Middleware для измерения времени запросов и кэширования.
"""

import time
from django.core.cache import cache
from django.db import connection
import json
import hashlib

class CacheMetricsMiddleware:
    """
    Middleware для сбора метрик по кэшированию.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        initial_queries = len(connection.queries) if hasattr(connection, 'queries') else 0
        response = self.get_response(request)

        end_time = time.time()
        request_time = end_time - start_time

        if hasattr(connection, 'queries'):
            total_queries = len(connection.queries) - initial_queries
        else:
            total_queries = 0

        response['X-Request-Time'] = f'{request_time:.3f}s'
        response['X-SQL-Queries'] = str(total_queries)

        if request.path.startswith('/api'):
            self._save_metrics(request.path, request_time, total_queries)

        return response
    
    def _save_metrics(self, path, request_time, query_count):
        """
        Сохраняет метрики в Redis для последующего анализа.
        """
        try:
            cache_key = f'request_metrics:{hashlib.md5(path.encode()).hexdigest()}'
            metrics = cache.get(cache_key,{
                'path': path,
                'count': 0,
                'total_time': 0,
                'total_queries': 0,
                'avg_time': 0.0,
                'avg_queries': 0.0,
            })

            metrics['count'] += 1
            metrics['total_time'] += request_time
            metrics['total_queries'] += query_count
            metrics['avg_time'] = metrics['total_time'] / metrics['count']
            metrics['avg_queries'] = metrics['total_queries'] / metrics['count']

            cache.set(cache_key, metrics, 60 * 60)

        except Exception:
            pass

class QueryCacheMiddleware:
    """
    Middleware для кэширования часто используемых запросов API.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.cacheable_paths = [
            '/api/products',
            '/api/user/contact',
            '/api/orders',
        ]

    def __call__(self, request):
        if request.method == 'GET' and any(request.path.startswith(p) for p in self.cacheable_paths):
            cache_key = self._generate_cache_key(request)

            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            response = self.get_response(request)

            if response.status_code == 200:
                timeout = self._get_cache_timeout(request.path)
                cache.set(cache_key, response, timeout)
            
            return response
        
        return self.get_response(request)
    
    def _generate_cache_key(self, request):
        """
        Генерирует ключ кэша на основе запроса.
        """
        key_data = {
            'path': request.path,
            'query': dict(request.GET),
            'user_id': str(request.user.id) if request.user.is_authenticated else 'annonymous',
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f'api_cache:{hashlib.sha256(key_string.encode()).hexdigest()}'
    
    def _get_cache_timeout(self, path):
        """
        Возвращает время кэширования в зависимости от endpoint.
        """
        if '/api/products' in path:
            return 60 * 5
        elif '/api/user/contact' in path:
            return 60 * 30
        elif '/api/orders' in path:
            return 60 * 2
        return 60 