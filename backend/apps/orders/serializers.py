from rest_framework import serializers
from decimal import Decimal
from datetime import time
from django.utils import timezone
from .models import Order, OrderItem, OrderItemModifier
from apps.products.models import Product, Modifier, StopList
from apps.users.models import DeliveryAddress
from apps.organizations.models import PaymentType, Terminal


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
        
        # Валидация модификаторов: проверяем только переданные (опциональные).
        # Обязательные (is_required или min_amount > 0) добавляются автоматически в OrderService.
        modifiers_data = attrs.get('modifiers', [])
        if modifiers_data:
            product_modifiers = {
                m.modifier_id: m
                for m in Modifier.objects.filter(product=product)
            }
            for mod_data in modifiers_data:
                modifier_id = mod_data.get('modifier_id')
                quantity = mod_data.get('quantity', 1)
                if not modifier_id:
                    raise serializers.ValidationError({
                        'modifiers': 'Не указан modifier_id'
                    })
                modifier = product_modifiers.get(modifier_id)
                if not modifier:
                    raise serializers.ValidationError({
                        'modifiers': f'Модификатор {modifier_id} не найден для этого продукта'
                    })
                if quantity < modifier.min_amount:
                    raise serializers.ValidationError({
                        'modifiers': f'Минимальное количество для {modifier.modifier_name}: {modifier.min_amount}'
                    })
                if quantity > modifier.max_amount:
                    raise serializers.ValidationError({
                        'modifiers': f'Максимальное количество для {modifier.modifier_name}: {modifier.max_amount}'
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
    payment_type_name = serializers.CharField(source='payment_type.payment_name', read_only=True)
    payment_type_system_type = serializers.CharField(source='payment_type.system_type', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'order_number', 'user', 'user_name',
            'organization', 'organization_name',
            'status', 'status_display', 'total_amount', 'total_price',
            'delivery_cost',
            'phone', 'items_count',
            'payment_type', 'payment_type_name', 'payment_type_system_type',
            'comment',
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
    payment_type_system_type = serializers.CharField(source='payment_type.system_type', read_only=True)
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
            'delivery_cost',
            'delivery_address', 'delivery_address_full',
            'phone', 'comment',
            'payment_type', 'payment_type_name', 'payment_type_system_type',
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
    delivery_type = serializers.ChoiceField(
        choices=[('delivery', 'Доставка'), ('pickup', 'Самовывоз')],
        required=False,
        default='delivery'
    )
    delivery_address_id = serializers.UUIDField(required=False, allow_null=True)
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=''
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default=''
    )
    payment_type_id = serializers.UUIDField(required=False, allow_null=True)
    terminal_id = serializers.UUIDField(required=False, allow_null=True)
    items = OrderItemCreateSerializer(many=True)

    # Оплата удалённым счётом (Kaspi и др.)
    remote_payment_phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=''
    )
    save_billing_phone = serializers.BooleanField(
        required=False,
        default=False
    )
    
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
    
    # Сумма доставки (если фронтенд её уже посчитал)
    delivery_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    
    def validate_payment_type_id(self, value):
        """Проверка типа оплаты (если передан)"""
        if value is None:
            return value
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            org_id = request.user.organization_id
            if org_id:
                try:
                    PaymentType.objects.get(
                        payment_id=value,
                        organization_id=org_id,
                        is_active=True
                    )
                    return value
                except PaymentType.DoesNotExist:
                    raise serializers.ValidationError('Тип оплаты не найден или недоступен')
        return value
    
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
    
    def validate_terminal_id(self, value):
        """Проверка терминала и рабочего времени"""
        if value:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                try:
                    terminal = Terminal.objects.get(terminal_id=value)
                    
                    # Проверяем рабочее время в часовом поясе проекта (TIME_ZONE, напр. Asia/Almaty)
                    working_hours = terminal.working_hours
                    if working_hours and working_hours.get('start') and working_hours.get('end'):
                        now_local = timezone.localtime(timezone.now())
                        current_time_str = now_local.strftime('%H:%M')
                        
                        # Преобразуем время в минуты для удобства сравнения
                        def time_to_minutes(time_str: str) -> int:
                            hours, minutes = map(int, time_str.split(':'))
                            return hours * 60 + minutes
                        
                        current_minutes = time_to_minutes(current_time_str)
                        start_minutes = time_to_minutes(working_hours['start'])
                        end_minutes = time_to_minutes(working_hours['end'])
                        
                        # Проверяем, находится ли текущее время в рабочем диапазоне
                        is_working_time = False
                        
                        if start_minutes <= end_minutes:
                            # Обычный случай: рабочее время в пределах одного дня (например, 09:00 - 22:00)
                            is_working_time = start_minutes <= current_minutes < end_minutes
                        else:
                            # Переход через полночь (например, 18:00 - 04:00)
                            # Рабочее время: с 18:00 до 23:59 или с 00:00 до 04:00
                            is_working_time = current_minutes >= start_minutes or current_minutes < end_minutes
                        
                        if not is_working_time:
                            raise serializers.ValidationError(
                                f'Извините, мы сейчас не принимаем заказы. Время работы: с {working_hours["start"]} до {working_hours["end"]}'
                            )
                    
                    return value
                except Terminal.DoesNotExist:
                    raise serializers.ValidationError('Терминал не найден')
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
        terminal_id = attrs.get('terminal_id')
        phone = (attrs.get('phone') or '').strip()
        payment_type_id = attrs.get('payment_type_id')

        # Телефон обязателен только при доставке или при оплате удалённым счётом (Kaspi). При наличных — не требуется.
        if delivery_address_id and not phone:
            raise serializers.ValidationError({'phone': 'Укажите номер телефона для связи при доставке'})
        if payment_type_id:
            request = self.context.get('request')
            org_id = request.user.organization_id if request and hasattr(request, 'user') else None
            if org_id:
                try:
                    payment_type = PaymentType.objects.get(
                        payment_id=payment_type_id,
                        organization_id=org_id,
                        is_active=True
                    )
                    system_type = (payment_type.system_type or '').strip()
                    if system_type == 'remote_payment':
                        remote_phone = (attrs.get('remote_payment_phone') or '').strip()
                        if not phone and not remote_phone:
                            raise serializers.ValidationError({'phone': 'Укажите номер телефона для выставления удалённого счёта'})
                except PaymentType.DoesNotExist:
                    pass

        # Адрес обязателен только при доставке (при самовывозе не требуем)
        delivery_type = (attrs.get('delivery_type') or 'delivery').strip().lower()
        if delivery_type == 'delivery' and not delivery_address_id:
            if not (latitude and longitude) and not (street_id and house):
                raise serializers.ValidationError(
                    {'delivery_address_id': 'Необходимо указать адрес доставки, координаты или данные улицы и дома'}
                )
        
        # Если terminal_id не указан, но у пользователя есть терминалы, проверяем первый
        request = self.context.get('request')
        if not terminal_id and request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'terminals') and user.terminals.exists():
                terminal = user.terminals.filter(is_active=True).first()
                if terminal:
                    working_hours = terminal.working_hours
                    if working_hours and working_hours.get('start') and working_hours.get('end'):
                        now_local = timezone.localtime(timezone.now())
                        current_time_str = now_local.strftime('%H:%M')
                        start_str = working_hours['start']
                        end_str = working_hours['end']

                        def time_to_minutes(t_str):
                            parts = t_str.split(':')
                            return int(parts[0]) * 60 + int(parts[1]) if len(parts) >= 2 else 0

                        current_minutes = time_to_minutes(current_time_str)
                        start_minutes = time_to_minutes(start_str)
                        end_minutes = time_to_minutes(end_str)

                        is_working_time = (
                            current_minutes >= start_minutes and current_minutes < end_minutes
                            if start_minutes <= end_minutes
                            else current_minutes >= start_minutes or current_minutes < end_minutes
                        )
                        if not is_working_time:
                            raise serializers.ValidationError(
                                f'Извините, мы сейчас не принимаем заказы. Время работы: с {start_str} до {end_str}'
                            )
        return attrs