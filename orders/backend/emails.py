"""
Функции для отправки email уведомлений через Celery.

Содержит функции-обертки для запуска асинхронных задач Celery.
"""

from .tasks import send_registration_email_task, send_order_confirmation_email_task


def send_registration_email(user_email, user_name):
    """
    Запускает асинхронную задачу для отправки приветственного письма.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
    """

    task = send_registration_email_task.delay(user_email, user_name)
    print(f'Задача отправки регистрационного email запущена: {task.id}')
    return task.id
    

def send_order_confirmation_email(user_email, user_name, order_id):
    """
    Запускает асинхронную задачу для отправки письма с подтверждением заказа.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
        order_id (int): ID заказа
    """

    task = send_order_confirmation_email_task.delay(user_email, user_name, order_id)
    print(f'Задача отправки подтверждения заказа #{order_id} запущена: {task.id}')
    return task.id


