"""
Модуль административного интерфейса Django для приложения.

Содержит кастомизированные классы ModelAdmin для всех моделей приложения,
настроенные для удобного отображения, фильтрации и поиска в админ-панели.

Зарегистрированные модели:
- Shop: Список магазинов
- Category: Список категорий товаров
- Product: Список продуктов
- ProductInfo: Информационный список о продуктах
- Parameter: Список имен параметров
- ProductParameter: Список параметров
- Contact: Список контактов пользователя
- Order: Список заказов
- OrderItem: Список заказанных позиций
"""

from django.contrib import admin
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Shop.
    
    Отображает колонки:
    - id: Идентификатор магазина
    - name: Название магазина
    - url: Ссылка на магазин
    
    Поиск осуществляется по полю name.
    """
    list_display = ('id', 'name', 'url')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Category.
    
    Отображает колонки:
    - id: Идентификатор категории
    - name: Название категории
    
    Поиск осуществляется по полю name.
    Использует горизонтальный виджет для выбора связанных магазинов.
    """
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('shops',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Product.
    
    Отображает колонки:
    - id: Идентификатор продукта
    - name: Название продукта
    - category: Категория продукта
    
    Фильтрация доступна по категории.
    Поиск осуществляется по полю name.
    """
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели ProductInfo.
    
    Отображает колонки:
    - id: Идентификатор записи
    - product: Продукт
    - shop: Магазин
    - price: Цена
    - quantity: Количество на складе
    
    Фильтрация доступна по магазину.
    Поиск осуществляется по названию продукта и модели.
    """
    list_display = ('id', 'product', 'shop', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')
    
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Parameter.
    
    Отображает колонки:
    - id: Идентификатор параметра
    - name: Название параметра
    
    Поиск осуществляется по полю name.
    """
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели ProductParameter.
    
    Отображает колонки:
    - id: Идентификатор записи
    - product_info: Информация о продукте
    - parameter: Параметр
    - value: Значение параметра
    
    Фильтрация доступна по параметру.
    Поиск осуществляется по значению параметра.
    """
    list_display = ('id', 'product_info', 'parameter', 'value')
    list_filter = ('parameter',)
    search_fields = ('value',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Contact.
    
    Отображает колонки:
    - id: Идентификатор контакта
    - user: Пользователь
    - street: Улица
    - house: Дом
    - phone: Телефон
    
    Поиск осуществляется по городу, улице и email пользователя.
    """
    list_display = ('id', 'user', 'street', 'house', 'phone')
    search_fields = ('city', 'street', 'user__email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Order.
    
    Отображает колонки:
    - id: Идентификатор заказа
    - user: Пользователь
    - dt: Дата и время создания
    - state: Статус заказа
    
    Фильтрация доступна по статусу и дате.
    Поиск осуществляется по email пользователя.
    """
    list_display = ('id', 'user', 'dt', 'state')
    list_filter = ('state', 'dt')
    search_fields = ('user__email',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели OrderItem.
    
    Отображает кастомные колонки:
    - id: Идентификатор позиции
    - get_order: Форматированное отображение заказа
    - get_product: Название продукта
    - get_shop: Название магазина
    - quantity: Количество товара
    
    Поиск осуществляется по email пользователя и названию продукта.
    """
    list_display = ('id', 'get_order', 'get_product', 'get_shop', 'quantity')
    search_fields = ('order__user__email', 'product_info__product__name')
    
    def get_order(self, obj):
        """
        Возвращает отформатированную строку с информацией о заказе.
        
        Args:
            obj: Объект OrderItem
            
        Returns:
            str: Строка в формате "Заказ #{id} от {дата}"
        """
        return f"Заказ #{obj.order.id} от {obj.order.dt.strftime('%d.%m.%Y %H:%M')}"
    get_order.short_description = 'Заказ'
    
    def get_product(self, obj):
        """
        Возвращает название продукта из связанной информации о продукте.
        
        Args:
            obj: Объект OrderItem
            
        Returns:
            str: Название продукта
        """
        return obj.product_info.product.name
    get_product.short_description = 'Продукт'
    
    def get_shop(self, obj):
        """
        Возвращает название магазина из связанной информации о продукте.
        
        Args:
            obj: Объект OrderItem
            
        Returns:
            str: Название магазина
        """
        return obj.product_info.shop.name
    get_shop.short_description = 'Магазин'
