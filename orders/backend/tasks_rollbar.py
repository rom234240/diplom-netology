"""
Celery задачи для тестирования Rollbar.
"""

from celery import shared_task
import time
import rollbar
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def test_rollbar_celery_task(self):
    """
    Тестовая Celery задача для проверки интеграции с Rollbar.
    """
    try:
        logger.info('Запуск тестовой Celery задачи для Rollbar')
        time.sleep(2)
        result = 100 / 0
        return f'Результат: {result}'
    
    except ZeroDivisionError as e:
        rollbar.report_exc_info()
        logger.error(f'Ошибка в Celery задаче отправлена в Rollbar: {str(e)}')
        raise self.retry(exc=e, countdown=60)
    
@shared_task
def send_rollbar_massage_task(message, level='info'):
    """
    Отправляет сообщение в Rollbar через Celery.
    """
    try:
        rollbar.report_message(message, level)
        logger.info(f'Сообщение отправлено в Rollbar через Celery: {message}')
        return f"Сообщение '{message}' отправлено в Rollbar"
    except Exception as e:
        logger.error(f'Ошибка отправки сообщения в Rollbar: {str:(e)}')
        raise