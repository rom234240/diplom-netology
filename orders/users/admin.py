"""
Модуль административного интерфейса для кастомной модели пользователя.

Содержит кастомизированный класс CustomUserAdmin, который расширяет стандартный
UserAdmin для управления пользователями с email в качестве основного идентификатора.

Основные особенности:
- Использует email вместо username для аутентификации
- Добавляет бизнес-поля (компания, должность)
- Настраивает отображение, фильтрацию и формы в админ-панели
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомный административный интерфейс для модели User.
    
    Расширяет стандартный UserAdmin для работы с email-аутентификацией
    и дополнительными бизнес-полями пользователя.
    
    Attributes:
        list_display: Поля для отображения в списке пользователей
        list_filter: Поля для фильтрации списка пользователей
        ordering: Порядок сортировки пользователей по умолчанию
        fieldsets: Группировка полей на странице редактирования пользователя
        add_fieldsets: Поля на странице создания нового пользователя
    """
    list_display = ('email', 'first_name', 'last_name', 'company', 'position', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'company')
    ordering = ('email',
                )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal_info'), {'fields': ('first_name', 'last_name', 'company', 'position')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important_dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'company', 'position'),
        }),
    )

