"""
Функции для отправки email уведомлений.

Содержит функции для отправки email при регистрации и подтверждении заказов.
"""

from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user_email, user_name):
    """
    Отправляет приветственное письмо при регистрации пользователя.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
    """
    subject = 'Добро пожаловать в наш магазин!'
    message = f'''
    Уважаемый(ая) {user_name},

    Благодарим Вас за регистрацию в нашем магазине!

    Теперь вы можете:
    - Просматривать товары
    - Добавлять товары в корзину
    - Оформлять заказы
    - Отслеживать статус заказов

    С уважением,
    Команда магазина!
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_EMAIL,
        [user_email],
        fail_silently = False,
    )

def send_order_confirmation_email(user_email, user_name, order_id):
    """
    Отправляет письмо с подтверждением заказа.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
        order_id (int): ID заказа
    """
    subject = f'Подтверждение заказа #{order_id}'
    message = f'''
    Уважаемый(ая) {user_name},
    
    Ваш заказ #{order_id} успешно оформлен!
    
    Статус заказа: Новый
    Номер заказа: {order_id}
    
    Мы уведомим вас об изменении статуса заказа.
    
    С уважением,
    Команда магазина!
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )

