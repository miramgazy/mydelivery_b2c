from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderItemModifier
from apps.products.models import Product, Modifier, StopList
from apps.users.models import DeliveryAddress
from apps.organizations.models import PaymentType


class OrderItemModifierSerializer(serializers.ModelSerializer):
    """Сериализатор для модификаторов позиции заказа"""
    
    class Meta:
        model = OrderItemModifier
        fields = [
            'id', 'modifier', 'modifier_name',
            'quantity', 'price'
        ]
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции заказа"""
    modifiers = OrderItemModifierSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name',
            'quantity', 'price', 'total_price',
            'modifiers', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderItemCreateSerializer(serializers.Serializer):
    """Сериализатор для создания позиции заказа"""
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    modifiers = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    
    def validate_product_id(self, value):
        """Проверка существования продукта"""
        try:
            product = Product.objects.get(product_id=value)
            if not product.is_available:
                raise serializers.ValidationError('Продукт недоступен для заказа')
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError('Продукт не найден')
    
    def validate(self, attrs):
        """Валидация позиции заказа"""
        product_id = attrs.get('product_id')
        
        # Получаем продукт
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Продукт не найден'})
        
        # Проверяем стоп-лист с учетом terminal_id
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.organization:
            # Получаем terminal_id из данных заказа (если есть)
            terminal_id = None
            if hasattr(request, 'data') and isinstance(request.data, dict):
                terminal_id = request.data.get('terminal_id')
            
            stop_list_query = StopList.objects.filter(
                product=product,
                organization=request.user.organization
            )
            
            # Если указан terminal_id, проверяем по нему
            if terminal_id:
                try:
                    from apps.organizations.models import Terminal
                    terminal = Terminal.objects.get(terminal_id=terminal_id)
                    if stop_list_query.filter(terminal=terminal).exists():
                        raise serializers.ValidationError({
                            'product_id': f'Продукт "{product.product_name}" временно недоступен в выбранном филиале'
                        })
                except (Terminal.DoesNotExist, ValueError):
                    # Если terminal не найден, проверяем по организации
                    if stop_list_query.exists():
                        raise serializers.ValidationError({
                            'product_id': f'Продукт "{product.product_name}" временно недоступен'
                        })
            else:
                # Если terminal_id не указан, проверяем по организации
                if stop_list_query.exists():
                    raise serializers.ValidationError({
                        'product_id': f'Продукт "{product.product_name}" временно недоступен'
                    })
        
        # Валидация модификаторов
        modifiers_data = attrs.get('modifiers', [])
        if modifiers_data:
            for mod_data in modifiers_data:
                modifier_id = mod_data.get('modifier_id')
                quantity = mod_data.get('quantity', 1)
                
                if not modifier_id:
                    raise serializers.ValidationError({
                        'modifiers': 'Не указан modifier_id'
                    })
                
                try:
                    modifier = Modifier.objects.get(modifier_id=modifier_id, product=product)
                    
                    # Проверяем количество
                    if quantity < modifier.min_amount:
                        raise serializers.ValidationError({
                            'modifiers': f'Минимальное количество для {modifier.modifier_name}: {modifier.min_amount}'
                        })
                    
                    if quantity > modifier.max_amount:
                        raise serializers.ValidationError({
                            'modifiers': f'Максимальное количество для {modifier.modifier_name}: {modifier.max_amount}'
                        })
                    
                except Modifier.DoesNotExist:
                    raise serializers.ValidationError({
                        'modifiers': f'Модификатор {modifier_id} не найден для этого продукта'
                    })
        
        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка заказов"""
    id = serializers.UUIDField(source='order_id', read_only=True)
    user_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.org_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'order_number', 'user', 'user_name',
            'organization', 'organization_name',
            'status', 'status_display', 'total_amount', 'total_price',
            'phone', 'items_count',
            'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj):
        """Количество позиций в заказе"""
        return obj.items.count()
    
    def get_user_name(self, obj):
        """
        Best-effort имя клиента для админки/витрин:
        - full_name
        - first_name
        - telegram_username
        - username
        """
        user = getattr(obj, 'user', None)
        if not user:
            return "Клиент"
        name = (getattr(user, 'full_name', '') or '').strip()
        if name:
            return name
        first_name = (getattr(user, 'first_name', '') or '').strip()
        if first_name:
            return first_name
        tg = (getattr(user, 'telegram_username', '') or '').strip()
        if tg:
            return tg
        username = (getattr(user, 'username', '') or '').strip()
        if username:
            return username
        return "Клиент"


class OrderDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о заказе"""
    id = serializers.UUIDField(source='order_id', read_only=True)
    user_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.org_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_name = serializers.CharField(source='payment_type.payment_name', read_only=True)
    terminal_name = serializers.CharField(source='terminal.terminal_group_name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address_full = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'iiko_order_id', 'order_number',
            'user', 'user_name', 'organization', 'organization_name',
            'status', 'status_display', 'total_amount', 'total_price',
            'delivery_address', 'delivery_address_full',
            'phone', 'comment',
            'payment_type', 'payment_type_name',
            'terminal', 'terminal_name',
            'latitude', 'longitude',
            'items', 'sent_to_iiko_at', 'error_message',
            'iiko_delivery_number', 'correlation_id',
            'created_at', 'updated_at'
        ]
    
    def get_delivery_address_full(self, obj):
        """Полный адрес доставки"""
        if obj.delivery_address:
            return str(obj.delivery_address)
        return None
    
    def get_user_name(self, obj):
        user = getattr(obj, 'user', None)
        if not user:
            return "Клиент"
        name = (getattr(user, 'full_name', '') or '').strip()
        if name:
            return name
        first_name = (getattr(user, 'first_name', '') or '').strip()
        if first_name:
            return first_name
        tg = (getattr(user, 'telegram_username', '') or '').strip()
        if tg:
            return tg
        username = (getattr(user, 'username', '') or '').strip()
        if username:
            return username
        return "Клиент"


class OrderCreateSerializer(serializers.Serializer):
    """Сериализатор для создания заказа"""
    delivery_address_id = serializers.UUIDField(required=False, allow_null=True)
    phone = serializers.CharField(max_length=20)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    payment_type_id = serializers.UUIDField()
    terminal_id = serializers.UUIDField(required=False, allow_null=True)
    items = OrderItemCreateSerializer(many=True)
    
    # Координаты (если адрес не указан)
    latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        required=False, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7,
        required=False, allow_null=True
    )
    
    # Адрес вручную (если не используется сохраненный)
    street_id = serializers.UUIDField(required=False, allow_null=True)
    house = serializers.CharField(required=False, allow_blank=True, default='')
    flat = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_payment_type_id(self, value):
        """Проверка типа оплаты"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            org_id = request.user.organization_id
            if org_id:
                try:
                    payment_type = PaymentType.objects.get(
                        payment_id=value,
                        organization_id=org_id,
                        is_active=True
                    )
                    return value
                except PaymentType.DoesNotExist:
                    raise serializers.ValidationError('Тип оплаты не найден или недоступен')
        
        raise serializers.ValidationError('Необходимо указать организацию')
    
    def validate_delivery_address_id(self, value):
        """Проверка адреса доставки"""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    address = DeliveryAddress.objects.get(
                        id=value,
                        user=request.user
                    )
                    return value
                except DeliveryAddress.DoesNotExist:
                    raise serializers.ValidationError('Адрес доставки не найден')
        return value
    
    def validate_items(self, value):
        """Проверка позиций заказа"""
        if not value:
            raise serializers.ValidationError('Заказ должен содержать хотя бы одну позицию')
        
        if len(value) > 50:
            raise serializers.ValidationError('Максимальное количество позиций в заказе: 50')
        
        return value
    
    def validate(self, attrs):
        """Общая валидация заказа"""
        delivery_address_id = attrs.get('delivery_address_id')
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        street_id = attrs.get('street_id')
        house = attrs.get('house')
        
        # Должен быть указан либо адрес, либо координаты
        if not delivery_address_id:
            if not (latitude and longitude):
                if not (street_id and house):
                    raise serializers.ValidationError(
                        'Необходимо указать адрес доставки, координаты или данные улицы и дома'
                    )
        
        return attrs