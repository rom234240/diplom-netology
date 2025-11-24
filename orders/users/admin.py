from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'company', 'position', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'company')
    ordering = ('email')

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
    
