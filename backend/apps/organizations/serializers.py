from rest_framework import serializers
from .models import Organization, Terminal, Street, PaymentType


class TerminalSerializer(serializers.ModelSerializer):
    """Сериализатор для терминалов"""
    id = serializers.UUIDField(source='terminal_id', read_only=True)
    name = serializers.CharField(source='terminal_group_name', read_only=True)
    iiko_terminal_id = serializers.UUIDField(source='terminal_id', read_only=True)
    
    class Meta:
        model = Terminal
        fields = [
            'id', 'terminal_id', 'iiko_terminal_id', 'iiko_organization_id', 
            'terminal_group_name', 'name', 'is_active', 'organization',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'terminal_id', 'created_at', 'updated_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор для организаций"""
    terminals = TerminalSerializer(many=True, read_only=True)
    
    # Добавляем поля для совместимости с фронтендом
    id = serializers.UUIDField(source='org_id', read_only=True)
    name = serializers.CharField(source='org_name')
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'org_id', 'name', 'org_name', 'city',
            'iiko_organization_id', 'api_key',
            'phone', 'address',
            'terminals', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'org_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': False},  # Позволяем читать для отображения
        }


class StreetSerializer(serializers.ModelSerializer):
    """Сериализатор для улиц"""
    
    class Meta:
        model = Street
        fields = [
            'street_id', 'street_name', 'city',
            'organization', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['street_id', 'created_at', 'updated_at']


class PaymentTypeSerializer(serializers.ModelSerializer):
    """Сериализатор для типов оплаты"""
    id = serializers.UUIDField(source='payment_id', read_only=True)
    iiko_payment_id = serializers.UUIDField(source='payment_id', read_only=True)
    name = serializers.CharField(source='payment_name', read_only=True)
    
    class Meta:
        model = PaymentType
        fields = [
            'id', 'payment_id', 'iiko_payment_id',
            'name', 'payment_name', 'payment_type',
            'organization', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']


class ExternalMenuSerializer(serializers.Serializer):
    """Сериализатор для внешних меню из iiko"""
    id = serializers.UUIDField()
    external_menu_id = serializers.UUIDField()
    name = serializers.CharField()
