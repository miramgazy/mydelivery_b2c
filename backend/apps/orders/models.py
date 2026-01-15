import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Order(models.Model):
    """Заказ"""
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_DELIVERING = 'delivering'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_ERROR = 'error'
    
    # Iiko Creation Statuses
    STATUS_IN_PROGRESS = 'InProgress'
    STATUS_SUCCESS = 'Success'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтвержден'),
        (STATUS_PREPARING, 'Готовится'),
        (STATUS_DELIVERING, 'Доставляется'),
        (STATUS_COMPLETED, 'Завершен'),
        (STATUS_CANCELLED, 'Отменен'),
        (STATUS_ERROR, 'Ошибка'),
        (STATUS_IN_PROGRESS, 'В процессе iiko'),
        (STATUS_SUCCESS, 'Успешно создан в iiko'),
    ]
    
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iiko_order_id = models.UUIDField('ID заказа в iiko', null=True, blank=True)
    correlation_id = models.UUIDField('Correlation ID iiko', null=True, blank=True)
    iiko_delivery_number = models.CharField('Номер доставки iiko', max_length=100, blank=True, null=True)
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Организация',
        db_column='org_id'
    )
    
    status = models.CharField('Статус', max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    order_number = models.CharField('Номер заказа', max_length=100, blank=True, null=True)
    total_amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    
    delivery_address = models.ForeignKey(
        'users.DeliveryAddress',
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Адрес доставки',
        null=True,
        blank=True,
        db_column='delivery_address_id'
    )
    
    phone = models.CharField('Телефон', max_length=20)
    comment = models.TextField('Комментарий', blank=True, null=True)
    
    payment_type = models.ForeignKey(
        'organizations.PaymentType',
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Тип оплаты',
        null=True,
        blank=True,
        db_column='payment_type_id'
    )
    
    latitude = models.DecimalField('Широта (разовая)', max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField('Долгота (разовая)', max_digits=10, decimal_places=7, null=True, blank=True)
    
    terminal = models.ForeignKey(
        'organizations.Terminal',
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Терминал',
        null=True,
        blank=True,
        db_column='terminal_id'
    )
    
    sent_to_iiko_at = models.DateTimeField('Отправлен в iiko', null=True, blank=True)
    iiko_response = models.JSONField('Ответ от iiko', null=True, blank=True)
    error_message = models.TextField('Текст ошибки', blank=True, null=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['organization']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Заказ {self.order_number or self.order_id} ({self.get_status_display()})"


class OrderItem(models.Model):
    """Позиция заказа"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
        db_column='order_id'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Продукт',
        db_column='product_id'
    )
    product_name = models.CharField('Название продукта', max_length=255)
    quantity = models.IntegerField('Количество', default=1)
    price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        indexes = [
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class OrderItemModifier(models.Model):
    """Модификатор позиции заказа"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='modifiers',
        verbose_name='Позиция заказа',
        db_column='order_item_id'
    )
    modifier = models.ForeignKey(
        'products.Modifier',
        on_delete=models.PROTECT,
        related_name='order_usage',
        verbose_name='Модификатор',
        db_column='modifier_id'
    )
    modifier_name = models.CharField('Название модификатора', max_length=255)
    quantity = models.IntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'order_item_modifiers'
        verbose_name = 'Модификатор в заказе'
        verbose_name_plural = 'Модификаторы в заказе'
        indexes = [
            models.Index(fields=['order_item']),
        ]
    
    def __str__(self):
        return f"{self.modifier_name} x {self.quantity}"
