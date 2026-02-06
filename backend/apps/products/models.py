import uuid
from django.db import models


class Menu(models.Model):
    """Меню организации"""
    SOURCE_NOMENCLATURE = 'nomenclature'
    SOURCE_EXTERNAL = 'external'
    SOURCE_CHOICES = [
        (SOURCE_NOMENCLATURE, 'Номенклатура'),
        (SOURCE_EXTERNAL, 'Внешнее'),
    ]

    menu_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_name = models.CharField('Название', max_length=255)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name='Организация'
    )
    is_active = models.BooleanField('Активно', default=False)
    source_type = models.CharField(
        'Тип',
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_NOMENCLATURE
    )
    # Метаданные: external_menu_id, price_category_id, price_category_name для внешнего меню
    metadata = models.JSONField('Метаданные', blank=True, null=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        db_table = 'menus'
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'

    def __str__(self):
        return f"{self.menu_name} ({self.organization.org_name})"


class ProductCategory(models.Model):
    """Категории продуктов (подгруппы)"""
    subgroup_id = models.UUIDField(primary_key=True)
    subgroup_name = models.CharField('Название', max_length=255)
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Меню',
        blank=True,
        null=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Родительская категория',
        blank=True,
        null=True
    )
    order_index = models.IntegerField('Порядок', default=0)
    
    # Хранение исходных данных для синхронизации
    outer_data = models.JSONField('Данные из iiko', blank=True, null=True)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name = 'Категория продуктов'
        verbose_name_plural = 'Категории продуктов'
        ordering = ['order_index', 'subgroup_name']
    
    def __str__(self):
        parent_name = f"{self.parent.subgroup_name} -> " if self.parent else ""
        return f"{parent_name}{self.subgroup_name}"


class Product(models.Model):
    """Продукты (блюда). Один и тот же product_id из iiko может быть в разных меню (unique_together product_id + menu)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField('ID продукта (iiko)', db_index=True)
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Меню'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Организация'
    )
    
    product_name = models.CharField('Название', max_length=255)
    product_code = models.CharField('Код', max_length=100, blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name='Категория',
        blank=True,
        null=True
    )
    
    parent_group = models.CharField('Родительская группа (имя)', max_length=255, blank=True, null=True)
    
    measure_unit = models.CharField('Единица измерения', max_length=50, default='порция')
    has_modifiers = models.BooleanField('Есть модификаторы', default=False)
    is_available = models.BooleanField('Доступен', default=True)
    
    description = models.TextField('Описание', blank=True, null=True)
    image_url = models.CharField('URL изображения', max_length=500, blank=True, null=True)
    order_index = models.IntegerField('Порядок', default=0)
    
    type = models.CharField('Тип (Dish, Good, etc)', max_length=50, blank=True, null=True)
    
    # Хранение исходных данных
    outer_data = models.JSONField('Данные из iiko', blank=True, null=True)
    
    # Синхронизация с iiko
    updated_from_iiko = models.DateTimeField('Обновлено из iiko', blank=True, null=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['order_index', 'product_name']
        constraints = [
            models.UniqueConstraint(fields=['product_id', 'menu'], name='products_product_id_menu_uniq'),
        ]
        indexes = [
            models.Index(fields=['menu']),
            models.Index(fields=['organization']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.product_name} - {self.price} ₸"


class Modifier(models.Model):
    """Модификаторы продуктов"""
    modifier_id = models.UUIDField(primary_key=True)
    modifier_name = models.CharField('Название', max_length=255)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='modifiers',
        verbose_name='Продукт',
        blank=True,
        null=True
    )
    
    min_amount = models.IntegerField('Минимальное количество', default=0)
    max_amount = models.IntegerField('Максимальное количество', default=1)
    modifier_code = models.CharField('Код', max_length=100, blank=True, null=True)
    modifier_weight = models.DecimalField(
        'Вес',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    is_required = models.BooleanField('Обязательный', default=False)
    
    # Синхронизация с iiko
    updated_from_iiko = models.DateTimeField('Обновлено из iiko', blank=True, null=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'modifiers'
        verbose_name = 'Модификатор'
        verbose_name_plural = 'Модификаторы'
        indexes = [
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.modifier_name} ({self.product.product_name if self.product else 'N/A'})"


class StopList(models.Model):
    """Стоп-лист продуктов (недоступные для заказа)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stop_list_entries',
        verbose_name='Продукт'
    )
    product_name = models.CharField('Название продукта', max_length=255)
    balance = models.DecimalField(
        'Остаток',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Остаток продукта на складе'
    )
    terminal = models.ForeignKey(
        'organizations.Terminal',
        on_delete=models.CASCADE,
        related_name='stop_list',
        verbose_name='Терминал',
        null=True,
        blank=True
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='stop_list',
        verbose_name='Организация'
    )
    
    # Причина добавления в стоп-лист
    reason = models.TextField('Причина', blank=True, null=True)
    
    # Автоматически добавлен через синхронизацию
    is_auto_added = models.BooleanField('Добавлен автоматически', default=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'stop_list'
        verbose_name = 'Стоп-лист'
        verbose_name_plural = 'Стоп-лист'
        unique_together = [['product', 'terminal']]
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['terminal']),
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return f"{self.product_name} - остаток: {self.balance}"


class FastMenuGroup(models.Model):
    """Группа быстрого меню (подборка товаров)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название группы', max_length=255)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='fast_menu_groups',
        verbose_name='Организация'
    )
    is_active = models.BooleanField('Активна', default=True)
    order = models.PositiveIntegerField('Порядок сортировки', default=0)
    
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'fast_menu_groups'
        verbose_name = 'Группа быстрого меню'
        verbose_name_plural = 'Группы быстрого меню'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.organization.org_name})"


class FastMenuItem(models.Model):
    """Элемент быстрого меню (связь группы с товаром)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        FastMenuGroup,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Группа'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='fast_menu_items',
        verbose_name='Товар'
    )
    order = models.IntegerField('Порядок', default=0)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'fast_menu_items'
        verbose_name = 'Элемент быстрого меню'
        verbose_name_plural = 'Элементы быстрого меню'
        ordering = ['order', 'product__product_name']
        unique_together = [['group', 'product']]
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['product']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.group.name} - {self.product.product_name}"