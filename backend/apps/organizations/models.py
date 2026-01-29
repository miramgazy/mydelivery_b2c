import uuid
from django.db import models


class Terminal(models.Model):
    """Терминал (группа терминалов)"""
    terminal_id = models.UUIDField(primary_key=True)
    terminal_group_name = models.CharField('Название терминала', max_length=255, blank=True, null=True)
    
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='terminals',
        verbose_name='Организация',
        null=True,
        blank=True
    )
    iiko_organization_id = models.CharField('ID организации в iiko', max_length=255, blank=True, null=True)
    
    city = models.ForeignKey(
        'City',
        on_delete=models.SET_NULL,
        related_name='terminals',
        verbose_name='Город',
        null=True,
        blank=True
    )
    
    # Интервал обновления стоп-листа в минутах
    stop_list_interval_min = models.IntegerField(
        'Интервал обновления стоп-листа (мин)',
        default=30,
        help_text='Частота обновления стоп-листа в минутах'
    )
    
    # Зоны доставки (JSONB поле для хранения массива объектов зон)
    delivery_zones_conditions = models.JSONField(
        'Условия зон доставки',
        default=list,
        blank=True,
        null=True,
        help_text='Массив объектов зон доставки с координатами, названием, приоритетом, цветом и типом доставки'
    )
    
    # Рабочее время терминала
    working_hours = models.JSONField(
        'Рабочее время',
        default=dict,
        blank=True,
        null=True,
        help_text="Рабочее время терминала в формате {'start': 'HH:mm', 'end': 'HH:mm'}"
    )
    
    is_active = models.BooleanField('Активен', default=True)
    
    # Ссылка на Instagram терминала (для брендинга в TMA)
    instagram_link = models.URLField('Ссылка на Instagram', max_length=500, blank=True, null=True)
    
    # Глобальный переключатель для активации расчета стоимости доставки
    is_delivery_calculation_apply = models.BooleanField(
        'Применять расчет стоимости доставки',
        default=False,
        help_text='Если включено, для этого терминала будет применяться расчет стоимости доставки на основе зон'
    )
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'terminals'
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'
    
    def __str__(self):
        return self.terminal_group_name or str(self.terminal_id)


class Organization(models.Model):
    """Организация (ресторан)"""
    org_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_name = models.CharField('Название', max_length=255)
    api_key = models.CharField('API Key iiko', max_length=255, blank=True, null=True)
    iiko_organization_id = models.CharField('ID организации в iiko', max_length=255, blank=True, null=True)
    city = models.CharField('Город', max_length=100, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=50, blank=True, null=True)
    address = models.CharField('Адрес', max_length=500, blank=True, null=True)
    
    # Telegram Bot fields for multi-bot support
    bot_token = models.CharField('Токен Telegram бота', max_length=255, blank=True, null=True, unique=True)
    bot_username = models.CharField('Юзернейм Telegram бота', max_length=255, blank=True, null=True)
    
    is_active = models.BooleanField('Активна', default=True)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
    
    def __str__(self):
        return self.org_name


class City(models.Model):
    """Города справочника для доставки"""
    city_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название', max_length=255)
    iiko_city_id = models.UUIDField('ID в iiko', blank=True, null=True)
    
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name='Организация'
    )
    
    is_active = models.BooleanField('Активен', default=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'cities'
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        unique_together = [['organization', 'city_id']]

    def __str__(self):
        return f"{self.name} ({self.organization.org_name})"


class Street(models.Model):
    """Улицы справочника для доставки"""
    street_id = models.UUIDField(primary_key=True)
    street_name = models.CharField('Название', max_length=255)
    iiko_street_id = models.UUIDField('ID в iiko', blank=True, null=True)
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='streets',
        verbose_name='Город',
        null=True,
        blank=True
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='streets',
        verbose_name='Организация'
    )
    
    is_deleted = models.BooleanField('Удалена', default=False)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'streets'
        verbose_name = 'Улица'
        verbose_name_plural = 'Улицы'
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['street_name']),
        ]
    
    def __str__(self):
        return f"{self.street_name} ({self.organization.org_name})"


class PaymentType(models.Model):
    """Типы оплаты"""
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_name = models.CharField('Название', max_length=255)
    payment_type = models.CharField('Тип оплаты (код)', max_length=100)
    # Внутренний системный тип, чтобы фронтенд понимал бизнес-логику оплаты.
    # Примеры: "cash", "remote_payment", "card_on_delivery"
    system_type = models.CharField(
        'Системный тип',
        max_length=50,
        blank=True,
        null=True,
        help_text='Варианты: cash, remote_payment, card_on_delivery и др.'
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='payment_types',
        verbose_name='Организация'
    )
    
    is_active = models.BooleanField('Активен', default=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'payment_types'
        verbose_name = 'Тип оплаты'
        verbose_name_plural = 'Типы оплаты'
        unique_together = [['organization', 'payment_id']]
    
    def __str__(self):
        return f"{self.payment_name} ({self.organization.org_name})"
