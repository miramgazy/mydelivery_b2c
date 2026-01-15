from rest_framework import serializers
from .models import Menu, ProductCategory, Product, Modifier, StopList


class MenuSerializer(serializers.ModelSerializer):
    """Сериализатор для меню"""
    organization_name = serializers.CharField(source='organization.org_name', read_only=True)
    
    class Meta:
        model = Menu
        fields = [
            'menu_id', 'menu_name', 'organization', 
            'organization_name', 'is_active'
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    
    class Meta:
        model = ProductCategory
        fields = [
            'subgroup_id', 'subgroup_name', 'menu', 
            'order_index'
        ]


class ModifierSerializer(serializers.ModelSerializer):
    """Сериализатор для модификаторов"""
    id = serializers.UUIDField(source='modifier_id', read_only=True)
    name = serializers.CharField(source='modifier_name', read_only=True)
    description = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    is_available = serializers.BooleanField(default=True, read_only=True)
    
    class Meta:
        model = Modifier
        fields = [
            'id', 'modifier_id', 'name', 'modifier_name', 
            'description', 'product', 'product_name',
            'min_amount', 'max_amount', 'modifier_weight',
            'price', 'is_required', 'is_available'
        ]
    
    def get_description(self, obj):
        """Генерируем описание модификатора"""
        parts = []
        if obj.min_amount and obj.max_amount:
            parts.append(f"От {obj.min_amount} до {obj.max_amount}")
        if obj.is_required:
            parts.append("Обязательно")
        return " | ".join(parts) if parts else None



class ProductListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка продуктов"""
    id = serializers.UUIDField(source='product_id', read_only=True)
    name = serializers.CharField(source='product_name', read_only=True)
    category = ProductCategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'product_name', 'price',
            'description', 'image_url', 'category',
            'is_available', 'has_modifiers', 'order_index'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о продукте"""
    id = serializers.UUIDField(source='product_id', read_only=True)
    name = serializers.CharField(source='product_name', read_only=True)
    category = ProductCategorySerializer(read_only=True)
    modifiers = ModifierSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'product_name', 'product_code',
            'price', 'measure_unit', 'description',
            'image_url', 'category',
            'is_available', 'has_modifiers', 'modifiers',
            'organization', 'order_index'
        ]


class StopListSerializer(serializers.ModelSerializer):
    """Сериализатор для стоп-листа"""
    product_name = serializers.CharField()
    
    class Meta:
        model = StopList
        fields = [
            'id', 'product', 'product_name',
            'balance', 'organization',
            'reason', 'is_auto_added',
            'updated_at'
        ]
