"""
API endpoints для тестирования Rollbar.
"""

from venv import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import rollbar
import logging


class RollbarTestView(APIView):
    """
        API endpoint для тестирования Rollbar.
        Генерирует различные типы ошибок для проверки мониторинга.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Возвращает список доступных тестовых ошибок.
        """
        return Response({
            'status': True,
            'message': 'Доступные тесты Rollbar',
            'tests': {
                'unhandled_exception': 'GET /api/rollbar/test/unhandled/ - Необработанное исключенин',
                'handled_exception': 'GET /api/rollbar/test/handled/ - Обработанное исключение',
                'log_error': 'GET /api/rollbar/test/log/error/ - Логирование ошибки',
                'log_warning': 'GET /api/rollbar/test/log/warning/ - Логирование предупреждения',
                'log_info': 'GET /api/rollbar/test/log/info/ - Логирование информации',
                'divide_by_zero': 'GET /api/rollbar/test/zero/ - Деление на ноль',
                'key_error': 'GET /api/rollbar/test/keyerror/ - Ошибка ключа',
                'attribute_error': 'GET /api/rollbar/test/attribute/ - Ошибка атрибута',
                'custom_message': 'GET /api/rollbar/test/custom/ - Кастомное сообщение', 
            }
        })
    
class RollbarUnhandledExceptionView(APIView):
    """
    Генерирует необработанное исключение для тестирования Rollbar.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Генерирует необработанное исключение.
        """
        raise Exception('Тестовое необработанное исключение для Rollbar')
    
class RollbarHandledExceptionView(APIView):
    """
    Генерирует обработанное исключение с логированием в Rollbar.
    """
    permissions_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Генерирует и обрабатывает исключение с отправкой в Rollbar.
        """
        try:
            raise ValueError('Тестовое обработанное исключение для Rollbar')
        except ValueError as e:
            rollbar.report_exc_info()
            logger.error(f'Обработанная ошибка отправлена в Rollbar: {str(e)}')

            return Response({
                'status': False,
                'error': str(e),
                'message': 'Исключение было обработано и отпралено в Rollbar'
            }, status=status.HTTP_400_BAD_REQUEST)
        
class RollbarLogTestView(APIView):
    """
    Тестирует различные уровни логирования.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Тестирует логирование разных уровней.
        """
        level = kwargs.get('level', 'error')

        if level == 'error':
            logger.error('Тестовое сообщение ERROR уровня для Rollbar')
            mesage = 'Сообщение ERROR уровня отправлено'
        elif level == 'warning':
            logger.warning('Тестовое сообщение WARNING уровня для Rollbar')
            message = 'Сообщение WARNING уровня отправлено'
        elif level == 'info':
            logger.info('Тестовое сообщение INFO уровня для Rollbar')
            message = 'Сообщение INFO уровня отправлено'
        elif level == 'debug':
            logger.debug('Тестовое сообщение DEBUG уровня для Rollbar')
            message = 'Сообщение DEBUG уровня отправлено'
        else:
            message = 'Неизвестный уровень логирования'

        return Response({
            'status': True,
            'message': message,
            'level': level
        })
    
class RollbarCustomMessageView(APIView):
    """
    Отправляет кастомные сообщения в Rollbar.
    """
    permisson_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Отправляет кастомное сообщение в Rollbar.
        """
        message = request.data.get('level', 'info')
        level = request.data.get('level', 'info')

        rollbar.report_message(message, level)

        return Response({
            'status': True,
            'messages': 'Кастомное сообщение отправлено в Rollbar',
            'data': {
                'text': message,
                'level': level
            }
        })
    
class RollbarDivideByZeroView(APIView):
    """
    Генерирует ошибку деления на ноль.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Делит на ноль для генерации ZeroDivisionError.
        """
        result = 10 / 0
        return Response({'result': result})
    
class RollbarKeyErrorView(APIView):
    """
    Генерирует ошибку KeyError.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Генерирует KeyError.
        """
        my_dict = {'key': 'value'}
        value = my_dict['nonexistent_key']
        return Response[{'value': value}]
    
class RollbarAttributeErrorView(APIView):
    """
    Генерирует ошибку AttributeError.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Генерирует AttributeError.
        """
        class TestClass:
            pass

        obj = TestClass()
        value = obj.nonexistent_attribute
        return Response({'value': value})

class RollbarCeleryTestView(APIView):
    """
    Тестирует интеграцию Rollbar с Celery.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Запускает Celery задачу с возможной ошибкой.
        """
        from .tasks import test_rollbar_celery_task

        task = test_rollbar_celery_task.delay()

        return Response({
            'status': True,
            'message': 'Celery задача запущена для тестирования Rollbar',
            'task_id': task.id
        })