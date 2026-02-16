from rest_framework import serializers
from .models import User, Role, DeliveryAddress, BillingPhone
from apps.organizations.serializers import TerminalSerializer
from apps.organizations.models import Terminal, City


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для ролей"""
    
    class Meta:
        model = Role
        fields = ['id', 'role_name', 'description']
        read_only_fields = ['id']


class DeliveryAddressSerializer(serializers.ModelSerializer):
    """Сериализатор для адресов доставки"""
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryAddress
        fields = [
            'id', 'user', 'city', 'city_name', 'iiko_city_id',
            'street', 'street_name', 'iiko_street_id',
            'house', 'flat', 'entrance', 'floor',
            'latitude', 'longitude', 'comment',
            'is_default', 'is_verified', 'full_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_full_address(self, obj):
        """Полный адрес в строковом виде"""
        return str(obj)
    
    def validate(self, attrs):
        """Валидация адреса и координат"""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise serializers.ValidationError({
                'latitude': 'Широта должна быть в диапазоне от -90 до 90'
            })
        
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise serializers.ValidationError({
                'longitude': 'Долгота должна быть в диапазоне от -180 до 180'
            })
        
        # Если передан city (ID города из справочника), но не передан city_name,
        # автоматически заполняем city_name из выбранного города
        city_id = attrs.get('city')
        city_name = attrs.get('city_name')
        
        if city_id and not city_name:
            try:
                # city_id может быть UUID или объектом City
                if isinstance(city_id, City):
                    attrs['city_name'] = city_id.name
                else:
                    # Если это ID, получаем объект
                    city = City.objects.get(city_id=city_id)
                    attrs['city_name'] = city.name
            except City.DoesNotExist:
                pass  # Если город не найден, оставляем city_name пустым
        
        return attrs


class BillingPhoneSerializer(serializers.ModelSerializer):
    """Сериализатор для дополнительных биллинг‑номеров"""

    class Meta:
        model = BillingPhone
        fields = [
            'id', 'user', 'phone', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""
    role_name = serializers.CharField(source='role.role_name', read_only=True, default=None)
    role_display = serializers.CharField(source='role.get_role_name_display', read_only=True, default=None)
    organization_name = serializers.CharField(source='organization.org_name', read_only=True, default=None)
    organization_bot_username = serializers.SerializerMethodField()

    def get_organization_bot_username(self, obj):
        if obj.organization and obj.organization.bot_username:
            return obj.organization.bot_username.lstrip('@')
        return None
    full_name = serializers.CharField(read_only=True)
    terminals = serializers.SerializerMethodField()
    addresses = DeliveryAddressSerializer(many=True, read_only=True)
    billing_phones = serializers.SerializerMethodField()
    
    def get_terminals(self, obj):
        """Возвращает только активные терминалы пользователя"""
        active_terminals = obj.terminals.filter(is_active=True)
        return TerminalSerializer(active_terminals, many=True).data
    
    def get_billing_phones(self, obj):
        """Возвращает биллинг-номера пользователя, безопасно обрабатывая случай отсутствия таблицы"""
        try:
            # Проверяем, есть ли у объекта доступ к billing_phones
            if hasattr(obj, 'billing_phones'):
                return BillingPhoneSerializer(obj.billing_phones.all(), many=True).data
            return []
        except Exception:
            # Если таблица не существует или произошла другая ошибка, возвращаем пустой список
            return []
    
    class Meta:
        model = User
        fields = [
            'id', 'telegram_id', 'first_name', 'last_name', 'username',
            'email', 'phone', 'telegram_username', 'full_name',
            'role', 'role_name', 'role_display',
            'organization', 'organization_name', 'organization_bot_username',
            'terminals', 'addresses', 'billing_phones',
            'iiko_user_id', 'language_code', 'is_active', 'last_login',
            'is_bot_subscribed', 'chat_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'telegram_id', 'created_at', 'updated_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    
    class Meta:
        model = User
        fields = [
            'telegram_id', 'first_name', 'last_name', 'username',
            'email', 'phone', 'telegram_username',
            'role', 'organization', 'iiko_user_id'
        ]
    
    def validate_telegram_id(self, value):
        """Проверка уникальности Telegram ID"""
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError('Пользователь с таким Telegram ID уже существует')
        return value
    
    def validate(self, attrs):
        """Валидация данных пользователя"""
        role = attrs.get('role')
        organization = attrs.get('organization')
        
        # Клиент может не иметь организацию при создании
        if role.role_name in [Role.ORG_ADMIN] and not organization:
            raise serializers.ValidationError({
                'organization': 'Администратор организации должен иметь привязку к организации'
            })
        
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления данных пользователя"""
    terminals = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Terminal.objects.all(),
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username',
            'email', 'phone', 'iiko_user_id', 'organization', 'terminals',
            'language_code'
        ]
    
    def validate_language_code(self, value):
        if value and value not in ('kz', 'ru'):
            raise serializers.ValidationError('Допустимые значения: kz, ru')
        return value or 'kz'

    def update(self, instance, validated_data):
        """Обновление пользователя с поддержкой терминалов"""
        terminals = validated_data.pop('terminals', None)
        
        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем терминалы, если они переданы
        if terminals is not None:
            instance.terminals.set(terminals)
        
        return instance


class TelegramAuthSerializer(serializers.Serializer):
    """Сериализатор для аутентификации через Telegram"""
    initData = serializers.CharField(required=True, write_only=True)
    
    # Возвращаемые данные
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)