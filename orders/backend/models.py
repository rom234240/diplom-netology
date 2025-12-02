"""
Модели приложения для управления магазинами, товарами и заказами.

Содержит все основные бизнес-модели:
- Shop: Магазины-партнеры
- Category: Категории товаров
- Product: Базовые товары
- ProductInfo: Конкретные предложения товаров в магазинах
- Parameter: Характеристики товаров
- ProductParameter: Значения характеристик для конкретных товаров
- Contact: Контактная информация пользователей
- Order: Заказы пользователей
- OrderItem: Позиции в заказах

Все модели содержат кастомизированные метаданные (verbose_name, ordering)
и реализуют метод __str__ для удобного отображения.
"""

from django.db import models
from users.models import User


class Shop(models.Model):
    """
    Модель магазина-партнера.
    
    Attributes:
        name (CharField): Название магазина (макс. 50 символов)
        url (URLField): Ссылка на сайт магазина (опционально)
    """
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    """
    Модель категории товаров.
    
    Attributes:
        name (CharField): Название категории (макс. 40 символов)
        shops (ManyToManyField): Магазины, в которых представлена категория
    """
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name
        
class Product(models.Model):
    """
    Модель базового товара (без привязки к магазину).
    
    Attributes:
        name (CharField): Название товара (макс. 80 символов)
        category (ForeignKey): Категория товара
    """
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return self.name
    
class ProductInfo(models.Model):
    """
    Модель информации о товаре в конкретном магазине (цена, остатки).
    
    Attributes:
        model (CharField): Модель/артикул товара (макс. 80 символов, опционально)
        external_id (PositiveIntegerField): Внешний идентификатор товара в магазине
        product (ForeignKey): Базовый товар
        shop (ForeignKey): Магазин
        quantity (PositiveIntegerField): Количество на складе
        price (PositiveIntegerField): Цена в магазине
        price_rrc (PositiveIntegerField): Рекомендуемая розничная цена
        
    Constraints:
        Уникальная комбинация product, shop и external_id
    """
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомедуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product_id', 'shop_id', 'external_id'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.shop.name}'

class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    """
    Модель связи значения параметра с конкретным товаром в магазине.
    
    Attributes:
        product_info (ForeignKey): Информация о товаре в магазине
        parameter (ForeignKey): Параметр/характеристика
        value (CharField): Значение параметра (макс. 100 символов)
        
    Constraints:
        Уникальная комбинация product_info и parameter
    """
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметер', related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info_id', 'parameter_id'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.product_info} - {self.parameter.name}'

# Константы для статусов заказов    
STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

class Contact(models.Model):
    """
    Модель контактной информации пользователя для доставки.
    
    Attributes:
        user (ForeignKey): Пользователь
        city (CharField): Город (макс. 50 символов)
        street (CharField): Улица (макс. 100 символов)
        house (CharField): Дом (макс. 15 символов, опционально)
        structure (CharField): Корпус (макс. 15 символов, опционально)
        building (CharField): Строение (макс. 15 символов, опционально)
        apartment (CharField): Квартира (макс. 15 символов, опционально)
        phone (CharField): Телефон (макс. 20 символов)
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='contacts',
        on_delete=models.CASCADE
    )
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'
    
class Order(models.Model):
    """
    Модель заказа пользователя.
    
    Attributes:
        user (ForeignKey): Пользователь, оформивший заказ
        dt (DateTimeField): Дата и время создания заказа (автоматически)
        state (CharField): Текущий статус заказа из STATE_CHOICES
        contact (ForeignKey): Контактная информация для доставки (опционально)
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='orders',
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(
        Contact,
        verbose_name='Контакт',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)
    
class OrderItem(models.Model):
    """
    Модель позиции (товара) в заказе.
    
    Attributes:
        order (ForeignKey): Заказ, к которому относится позиция
        product_info (ForeignKey): Информация о товаре в магазине (опционально)
        quantity (PositiveIntegerField): Количество товара в позиции
    """
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name = 'ordered_items',
        on_delete = models.CASCADE
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='order_items',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'
    
    def __str__(self):
        """
        Возвращает строковое представление позиции заказа.
        
        Если есть привязанный товар - возвращает название и количество.
        Если товар отсутствует - возвращает сообщение о пустом товаре.
        """
        if self.product_info:
            return f'{self.product_info.product.name} - {self.quantity} шт.'
        return f'Пустой товар - {self.quantity} шт.'
