from django.contrib import admin
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact, Order, OrderItem


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('shops',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shop', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')
    
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_info', 'parameter', 'value')
    list_filter = ('parameter',)
    search_fields = ('value',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'street', 'house', 'phone')
    search_fields = ('city', 'street', 'user__email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'state')
    list_filter = ('state', 'dt')
    search_fields = ('user__email',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order', 'get_product', 'get_shop', 'quantity')
    search_fields = ('order__user__email', 'product_info__product__name')
    
    def get_order(self, obj):
        return f"Заказ #{obj.order.id} от {obj.order.dt.strftime('%d.%m.%Y %H:%M')}"
    get_order.short_description = 'Заказ'
    
    def get_product(self, obj):
        return obj.product_info.product.name
    get_product.short_description = 'Продукт'
    
    def get_shop(self, obj):
        return obj.product_info.shop.name
    get_shop.short_description = 'Магазин'
