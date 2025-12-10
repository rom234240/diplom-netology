"""
Команда для тестирования производительности кэширования.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from backend.models import Product, Shop, Category, ProductInfo
import time
import statistics


class Command(BaseCommand):
    help = 'Тестирование производительности кэширования'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='Количество итераций для каждого теста'
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Очистить кэш перед тестированием'
        )
    
    def handle(self, *args, **options):
        iterations = options['iterations']
        
        if options['clear_cache']:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Кэш очищен'))
        
        self.stdout.write(self.style.SUCCESS(f'Запуск тестов производительности ({iterations} итераций)'))
        
        results = []
        
        # Тест 1: Простой запрос - все товары
        self.stdout.write('\n1. Тест: Product.objects.all()')
        db_times, cache_times = self._run_test(
            lambda: list(Product.objects.all()),
            iterations
        )
        results.append(('products_all', db_times, cache_times))
        
        # Тест 2: Запрос с фильтром
        self.stdout.write('\n2. Тест: Product.objects.filter(category_id=1)')
        db_times, cache_times = self._run_test(
            lambda: list(Product.objects.filter(category_id=1)),
            iterations
        )
        results.append(('products_filtered', db_times, cache_times))
        
        # Тест 3: Сложный запрос с JOIN
        self.stdout.write('\n3. Тест: Shop с продуктами')
        db_times, cache_times = self._run_test(
            lambda: list(Shop.objects.prefetch_related('product_infos__product')[:5]),
            iterations
        )
        results.append(('shops_with_products', db_times, cache_times))
        
        # Тест 4: Агрегация
        self.stdout.write('\n4. Тест: Количество товаров по категориям')
        from django.db.models import Count
        db_times, cache_times = self._run_test(
            lambda: list(Category.objects.annotate(product_count=Count('products'))),
            iterations
        )
        results.append(('category_stats', db_times, cache_times))
        
        # Вывод результатов
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        for name, db_times, cache_times in results:
            avg_db = statistics.mean(db_times)
            avg_cache = statistics.mean(cache_times)
            improvement = ((avg_db - avg_cache) / avg_db) * 100
            
            self.stdout.write(f'\n{name}:')
            self.stdout.write(f'  Без кэша:    {avg_db:.4f}s (мин: {min(db_times):.4f}s, макс: {max(db_times):.4f}s)')
            self.stdout.write(f'  С кэшем:     {avg_cache:.4f}s (мин: {min(cache_times):.4f}s, макс: {max(cache_times):.4f}s)')
            self.stdout.write(f'  Улучшение:   {improvement:.1f}%')
            
            if improvement > 0:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Кэширование эффективно'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ Кэширование не дало улучшения'))
    
    def _run_test(self, query_func, iterations):
        """
        Запускает тест с указанным количеством итераций.
        Возвращает время выполнения без кэша и с кэшем.
        """
        db_times = []
        cache_times = []
        
        for i in range(iterations):
            # Первый запуск - без кэша (или заполнение кэша)
            if i == 0:
                cache.clear()
            
            # Измеряем время без кэша (на первой итерации)
            start = time.time()
            query_func()
            db_time = time.time() - start
            db_times.append(db_time)
            
            # Измеряем время с кэшем (на всех итерациях)
            start = time.time()
            query_func()
            cache_time = time.time() - start
            cache_times.append(cache_time)
        
        return db_times, cache_times