from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user_email, user_name):
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
        file_silently = False,
    )

def send_order_confirmation_email(user_email, user_name, order_id):
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

