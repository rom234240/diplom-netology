from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_registration_email_task(self, user_email, user_name):
    """
    Асинхронная задача для отправки приветственного письма при регистрации.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
    """

    try:
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
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f'Email успешно отправлен на {user_email}'
    
    except Exception as e:
        self.retry(exc=e, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email_task(self, user_email, user_name, order_id):
    """
    Асинхронная задача для отправки письма с подтверждением заказа.
    
    Args:
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
        order_id (int): ID заказа
    """

    try:
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
        return f'Email подтверждение заказа #{order_id} отправлен на {user_email}'
    
    except Exception as e:
        self.retry(exc=e, countdown=60)