"""
Celery задачи для обработки изображений.
"""

from celery import shared_task
from django.core.files.storage import default_storage
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile


@shared_task(bind=True, max_retries=3)
def process_product_image(self, product_id):
    """
    Асинхронная обработка изображения товара.
    """
    from .models import Product
    
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.image:
            return f'Товар {product_id} не имеет изображения'
        
        print(f'Обработка изображения для товара: {product.name}')
        
        # Открываем изображение
        image_path = product.image.path
        with Image.open(image_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Сохраняем оптимизированную версию
            output = BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)
            
            # Сохраняем обратно
            file_name = os.path.basename(image_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            optimized_name = f"{file_name_without_ext}_optimized.jpg"
            
            # Сохраняем оптимизированную версию
            product.image.save(
                optimized_name,
                ContentFile(output.read()),
                save=False
            )
            product.save()
        
        print(f'Изображение товара {product.name} обработано')
        return f'Изображение товара {product_id} успешно обработано'
    
    except Exception as e:
        print(f'Ошибка обработки изображения товара {product_id}: {e}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_additional_image(self, image_id):
    """
    Асинхронная обработка дополнительного изображения.
    """
    from .models import ProductImage
    
    try:
        product_image = ProductImage.objects.get(id=image_id)
        
        if not product_image.image:
            return f'Изображение {image_id} не найдено'
        
        print(f'Обработка дополнительного изображения: {image_id}')
        
        # Аналогичная обработка
        image_path = product_image.image.path
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)
            
            file_name = os.path.basename(image_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            optimized_name = f"{file_name_without_ext}_optimized.jpg"
            
            product_image.image.save(
                optimized_name,
                ContentFile(output.read()),
                save=False
            )
            product_image.save()
        
        print(f'Дополнительное изображение {image_id} обработано')
        return f'Дополнительное изображение {image_id} успешно обработано'
    
    except Exception as e:
        print(f'Ошибка обработки дополнительного изображения {image_id}: {e}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_user_avatar(self, user_id):
    """
    Асинхронная обработка аватара пользователя.
    """
    from users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        if not user.avatar:
            return f'Пользователь {user_id} не имеет аватара'
        
        print(f'Обработка аватара пользователя: {user.email}')
        
        # Открываем и оптимизируем аватар
        avatar_path = user.avatar.path
        with Image.open(avatar_path) as img:
            # Конвертируем в квадрат если нужно
            width, height = img.size
            if width != height:
                # Обрезаем до квадрата
                size = min(width, height)
                left = (width - size) / 2
                top = (height - size) / 2
                right = (width + size) / 2
                bottom = (height + size) / 2
                img = img.crop((left, top, right, bottom))
            
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Сохраняем оптимизированную версию
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            file_name = os.path.basename(avatar_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            optimized_name = f"{file_name_without_ext}_optimized.jpg"
            
            user.avatar.save(
                optimized_name,
                ContentFile(output.read()),
                save=False
            )
            user.save()
        
        print(f'Аватар пользователя {user.email} обработан')
        return f'Аватар пользователя {user_id} успешно обработан'
    
    except Exception as e:
        print(f'Ошибка обработки аватара пользователя {user_id}: {e}')
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_orphaned_images():
    """
    Очистка orphaned изображений (без привязки к объектам).
    """
    import os
    from django.conf import settings
    from users.models import User
    from .models import Product, ProductImage
    
    print('Запуск очистки orphaned изображений...')
    
    # Получаем все существующие изображения из БД
    user_avatars = set()
    for user in User.objects.exclude(avatar=''):
        if user.avatar:
            user_avatars.add(user.avatar.name)
    
    product_images = set()
    for product in Product.objects.exclude(image=''):
        if product.image:
            product_images.add(product.image.name)
    
    additional_images = set()
    for img in ProductImage.objects.exclude(image=''):
        if img.image:
            additional_images.add(img.image.name)
    
    all_db_images = user_avatars.union(product_images, additional_images)
    
    # Проверяем файлы в media папке
    media_root = settings.MEDIA_ROOT
    orphaned_count = 0
    
    for root, dirs, files in os.walk(media_root):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)
                
                # Проверяем есть ли файл в БД
                if relative_path not in all_db_images:
                    # Проверяем не является ли это оптимизированной версией
                    is_optimized = '_optimized' in file or '_thumbnail' in file
                    
                    if not is_optimized:
                        try:
                            os.remove(file_path)
                            orphaned_count += 1
                            print(f'Удален orphaned файл: {relative_path}')
                        except Exception as e:
                            print(f'Ошибка удаления {relative_path}: {e}')
    
    print(f'Очистка завершена. Удалено файлов: {orphaned_count}')
    return f'Удалено {orphaned_count} orphaned изображений'


@shared_task
def generate_missing_thumbnails():
    """
    Генерация отсутствующих миниатюр.
    """
    from users.models import User
    from .models import Product, ProductImage
    
    print('Генерация отсутствующих миниатюр...')
    
    generated_count = 0
    
    # Генерация для пользователей
    for user in User.objects.exclude(avatar=''):
        if user.avatar:
            try:
                # Это заставит ImageKit сгенерировать миниатюры
                user.avatar_thumbnail.url
                user.avatar_small.url
                user.avatar_medium.url
                generated_count += 3
            except Exception as e:
                print(f'Ошибка генерации миниатюр для пользователя {user.id}: {e}')
    
    # Генерация для товаров
    for product in Product.objects.exclude(image=''):
        if product.image:
            try:
                product.image_thumbnail.url
                product.image_small.url
                product.image_medium.url
                product.image_large.url
                generated_count += 4
            except Exception as e:
                print(f'Ошибка генерации миниатюр для товара {product.id}: {e}')
    
    # Генерация для дополнительных изображений
    for img in ProductImage.objects.exclude(image=''):
        if img.image:
            try:
                img.thumbnail.url
                generated_count += 1
            except Exception as e:
                print(f'Ошибка генерации миниатюр для доп. изображения {img.id}: {e}')
    
    print(f'Сгенерировано миниатюр: {generated_count}')
    return f'Сгенерировано {generated_count} миниатюр'