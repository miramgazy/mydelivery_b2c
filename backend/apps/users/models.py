import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from apps.organizations.models import Organization, Street, Terminal


class Role(models.Model):
    """Роли пользователей"""
    SUPERADMIN = 'superadmin'
    ORG_ADMIN = 'org_admin'
    CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (SUPERADMIN, 'Суперадминистратор'),
        (ORG_ADMIN, 'Администратор организации'),
        (CUSTOMER, 'Клиент'),
    ]
    
    role_name = models.CharField('Название роли', max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField('Описание', blank=True, null=True)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
    
    def __str__(self):
        return self.get_role_name_display()


class User(AbstractUser):
    """Кастомная модель пользователя"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    telegram_id = models.BigIntegerField('Telegram ID', unique=True, null=True, blank=True)
    telegram_username = models.CharField('Telegram Username', max_length=255, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Роль',
        null=True,
        blank=True
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Организация',
        null=True,
        blank=True,
        db_column='org_id'
    )
    
    iiko_user_id = models.UUIDField('ID в iiko', null=True, blank=True)
    
    terminals = models.ManyToManyField(
        Terminal,
        related_name='users',
        verbose_name='Присвоенные терминалы',
        blank=True
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username or str(self.telegram_id)
        
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_superadmin(self):
        return self.is_superuser or (self.role and self.role.role_name == Role.SUPERADMIN)

    @property
    def is_org_admin(self):
        return self.role and self.role.role_name == Role.ORG_ADMIN

    @property
    def is_customer(self):
        return self.role and self.role.role_name == Role.CUSTOMER


class DeliveryAddress(models.Model):
    """Адреса доставки"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Пользователь'
    )
    city_name = models.CharField('Город', max_length=100)
    iiko_city_id = models.UUIDField('ID города iiko', null=True, blank=True)
    city = models.ForeignKey(
        'organizations.City',
        on_delete=models.SET_NULL,
        related_name='addresses',
        verbose_name='Город (из справочника)',
        null=True,
        blank=True
    )
    
    street_name = models.CharField('Улица', max_length=255, blank=True, null=True)
    iiko_street_id = models.UUIDField('ID улицы iiko', null=True, blank=True)
    
    street = models.ForeignKey(
        Street,
        on_delete=models.SET_NULL,
        related_name='addresses',
        verbose_name='Улица (из справочника)',
        null=True,
        blank=True,
        db_column='street_id'
    )
    
    house = models.CharField('Дом', max_length=50, blank=True, null=True)
    flat = models.CharField('Квартира/Офис', max_length=50, blank=True, null=True)
    entrance = models.CharField('Подъезд', max_length=50, blank=True, null=True)
    floor = models.CharField('Этаж', max_length=50, blank=True, null=True)
    
    latitude = models.DecimalField('Широта', max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField('Долгота', max_digits=10, decimal_places=7, null=True, blank=True)
    
    comment = models.TextField('Комментарий к адресу', blank=True, null=True)
    is_default = models.BooleanField('Основной', default=False)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'delivery_addresses'
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
    
    def __str__(self):
        parts = []
        city = self.city.name if self.city else self.city_name
        if city:
            parts.append(city)
        
        street = self.street_name or (self.street.street_name if self.street else None)
        if street:
            addr = street
            if self.house:
                addr += f", {self.house}"
            parts.append(addr)
        
        if self.flat:
            parts.append(f"кв./офис {self.flat}")
            
        if not parts and self.latitude and self.longitude:
            return f"Координаты: {self.latitude}, {self.longitude}"
            
        return ", ".join(parts)


class BillingPhone(models.Model):
    """Дополнительные номера телефонов для биллинга (Kaspi и др.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='billing_phones',
        verbose_name='Пользователь'
    )
    phone = models.CharField('Телефон', max_length=20)
    is_default = models.BooleanField('Основной', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        db_table = 'billing_phones'
        verbose_name = 'Биллинг‑номер'
        verbose_name_plural = 'Биллинг‑номера'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.phone} ({self.user})"

    def delete(self, using=None, keep_parents=False):
        """
        Запрещаем удаление, если у пользователя остался только один адрес.
        Это бизнес-правило для B2C UX (всегда должен оставаться минимум 1 адрес).
        """
        if self.user_id:
            remaining = DeliveryAddress.objects.filter(user_id=self.user_id).count()
            if remaining <= 1:
                raise ValidationError('Нельзя удалить последний адрес доставки')

        return super().delete(using=using, keep_parents=keep_parents)
