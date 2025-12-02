"""
Модуль кастомной модели пользователя для системы заказов.

Определяет кастомную модель пользователя с email-аутентификацией
вместо стандартного username и добавляет бизнес-поля (компания, должность).

Основные компоненты:
- UserManager: Кастомный менеджер пользователей для email-аутентификации
- User: Кастомная модель пользователя, наследуемая от AbstractUser
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManger(BaseUserManager):
    """
    Кастомный менеджер для модели User.
    
    Наследуется от BaseUserManager и переопределяет методы создания пользователей
    для работы с email в качестве основного идентификатора вместо username.
    
    Attributes:
        use_in_migrations: Указывает Django использовать этот менеджер в миграциях
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Внутренний метод для создания и сохранения пользователя.
        
        Args:
            email (str): Email пользователя (обязательное поле)
            password (str): Пароль пользователя
            **extra_fields: Дополнительные поля пользователя
        
        Returns:
            User: Созданный объект пользователя
        
        Raises:
            ValueError: Если email не предоставлен
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        username = email.split('@'[0])
        extra_fields.setdefault('username', username)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя (не персонал, не суперпользователь).
        
        Args:
            email (str): Email пользователя
            password (str): Пароль пользователя (опционально)
            **extra_fields: Дополнительные поля пользователя
        
        Returns:
            User: Созданный объект обычного пользователя
        """
        extra_fields.setdafault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Создает суперпользователя (администратора системы).
        
        Args:
            email (str): Email суперпользователя
            password (str): Пароль суперпользователя
            **extra_fields: Дополнительные поля пользователя
        
        Returns:
            User: Созданный объект суперпользователя
        
        Raises:
            ValueError: Если is_staff или is_superuser не установлены в True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    """
    Кастомная модель пользователя для системы заказов.
    
    Наследуется от AbstractUser и переопределяет стандартное поведение:
    - Использует email вместо username для аутентификации
    - Добавляет бизнес-поля (компания, должность)
    - Делает username опциональным полем
    
    Attributes:
        REQUIRED_FIELDS: Список обязательных полей (пустой, так как email - единственное обязательное)
        objects: Кастомный менеджер пользователей
        USERNAME_FIELD: Поле, используемое для аутентификации (email)
        
        email (EmailField): Уникальный email пользователя
        company (CharField): Название компании пользователя
        position (CharField): Должность пользователя
        username (CharField): Имя пользователя (опционально, автоматически генерируется из email)
        is_active (BooleanField): Флаг активности пользователя
    """
    REQUIRED_FIELDS = []
    objects = UserManger()
    USERNAME_FIELD = 'email'

    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)

    username = models.CharField(
        _('username'),
        max_length=150,
        blank=True,
        null=True,
        help_text=_('150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default = True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        """
        Строковое представление пользователя.
        
        Returns:
            str: Полное имя пользователя в формате "Имя Фамилия"
        """
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        """
        Метаданные модели пользователя.
        
        Attributes:
            verbose_name: Человекочитаемое имя модели в единственном числе
            verbose_name_plural: Человекочитаемое имя модели во множественном числе
            ordering: Порядок сортировки по умолчанию (по email)
        """
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)

