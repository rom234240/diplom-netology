from django.contrib import admin
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('shops',)
    list_per_page = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_display_links = ('id', 'name')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    list_per_page = 20

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1
    classes = ('colapse')

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shop', 'price', 'price_rrc', 'quantity', 'external_id')
    list_display_links = ('id', 'product')
    list_filter = ('shop', 'product__category')
    search_fields = ('product__name', 'model', 'external_id')
    raw_id_fields = ('product', 'shop')
    inlines = [ProductParameterInline]
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'shop')
    
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 20

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_info', 'parameter', 'value')
    list_display_links = ('id', 'product_info')
    list_filter = ('parameter',)
    search_fields = ('product_info__product__name', 'parameter__name', 'value')
    raw_id_fields = ('product_info', 'parameter')
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product_inf__product', 'parameter')
