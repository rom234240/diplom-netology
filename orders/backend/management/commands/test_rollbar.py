"""
Команда для тестирования Rollbar без реального токена.
"""

from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Тестирование Rollbar в локальном окружении'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Тестирование Rollbar...'))
        
        # Тест 1: Простое логирование
        logger.debug("Тестовое сообщение DEBUG уровня")
        logger.info("Тестовое сообщение INFO уровня")
        logger.warning("Тестовое сообщение WARNING уровня")
        logger.error("Тестовое сообщение ERROR уровня")
        
        self.stdout.write(self.style.SUCCESS('Логирование протестировано'))
        
        # Тест 2: Исключения
        try:
            raise ValueError("Тестовое исключение для проверки обработки ошибок")
        except ValueError as e:
            logger.exception(f"Перехваченное исключение: {e}")
        
        self.stdout.write(self.style.SUCCESS('Обработка исключений протестирована'))
        
        # Тест 3: Проверка настроек
        from django.conf import settings
        if hasattr(settings, 'ROLLBAR'):
            self.stdout.write(self.style.SUCCESS(f"Rollbar настроен: {settings.ROLLBAR.get('enabled', False)}"))
        else:
            self.stdout.write(self.style.WARNING("Rollbar не настроен в settings.py"))
        
        self.stdout.write(self.style.SUCCESS('Тестирование Rollbar завершено'))