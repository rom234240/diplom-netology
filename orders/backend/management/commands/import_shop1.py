import os
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
import yaml



class Command(BaseCommand):
    help = 'Импорт всех данных из shop1.yaml'

    def handle(self, *args, **options):
        self.stdout.write('=== Начало импорта ВСЕХ данных из shop1.yaml ===')
        
        yaml_path = os.path.join(os.path.dirname(__file__), '../../../shop1.yaml')
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                
            self.stdout.write(f"YAML файл загружен: {data['shop']}")
            self.stdout.write(f"Категорий: {len(data['categories'])}")
            self.stdout.write(f"Товаров: {len(data['goods'])}")
            
            shop, created = Shop.objects.get_or_create(name=data['shop'])
            if created:
                self.stdout.write(f"Создан магазин: {shop.name}")
            else:
                self.stdout.write(f"Найден существующий магазин: {shop.name}")
            
            category_count = 0
            for category_data in data['categories']:
                category, created = Category.objects.update_or_create(
                    id=category_data['id'],
                    defaults={'name': category_data['name']}
                )
                category.shops.add(shop)
                if created:
                    self.stdout.write(f"Создана категория: {category.name} (id: {category.id})")
                else:
                    self.stdout.write(f"Обновлена категория: {category.name} (id: {category.id})")
                category_count += 1
            
            deleted_count, _ = ProductInfo.objects.filter(shop=shop).delete()
            self.stdout.write(f"Удалено старых товаров: {deleted_count}")
            
            product_count = 0
            product_info_count = 0
            parameter_count = 0
            
            for item in data['goods']:
                product, created = Product.objects.update_or_create(
                    name=item['name'],
                    category_id=item['category'],
                    defaults={'name': item['name'], 'category_id': item['category']}
                )
                if created:
                    self.stdout.write(f"Создан продукт: {product.name}")
                product_count += 1
                
                product_info, created = ProductInfo.objects.update_or_create(
                    external_id=item['id'],
                    shop=shop,
                    defaults={
                        'product': product,
                        'model': item['model'],
                        'price': item['price'],
                        'price_rrc': item['price_rrc'],
                        'quantity': item['quantity']
                    }
                )
                if created:
                    self.stdout.write(f"Создана информация о продукте: {product.name}")
                product_info_count += 1
                
                for param_name, param_value in item['parameters'].items():
                    parameter, created = Parameter.objects.get_or_create(name=param_name)
                    if created:
                        self.stdout.write(f"Создан параметр: {parameter.name}")
                    
                    ProductParameter.objects.update_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': str(param_value)}
                    )
                    parameter_count += 1
            
            self.stdout.write('=== Импорт shop1.yaml завершен успешно! ===')
            
            self.stdout.write(f"ИТОГО ИМПОРТИРОВАНО:")
            self.stdout.write(f"Магазинов: {Shop.objects.count()}")
            self.stdout.write(f"Категорий: {Category.objects.count()}")
            self.stdout.write(f"Продуктов: {Product.objects.count()}")
            self.stdout.write(f"Записей ProductInfo: {ProductInfo.objects.count()}")
            self.stdout.write(f"Параметров: {Parameter.objects.count()}")
            self.stdout.write(f"Значений параметров: {ProductParameter.objects.count()}")
            
            self.stdout.write(f"ИЗ ФАЙЛА:")
            self.stdout.write(f"Обработано категорий: {category_count}")
            self.stdout.write(f"Обработано продуктов: {product_count}")
            self.stdout.write(f"Создано ProductInfo: {product_info_count}")
            self.stdout.write(f"Добавлено параметров: {parameter_count}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при импорте: {str(e)}'))
            import traceback
            traceback.print_exc()