from django.contrib import admin
from .models import Menu, ProductCategory, Product, Modifier, StopList, FastMenuGroup, FastMenuItem

class BaseProductAdmin(admin.ModelAdmin):
    """Базовый класс для админки с поддержкой UUID фильтров и прав доступа по организации"""
    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        org = getattr(request.user, 'organization', None)
        if not org:
            return qs.none()
            
        if self.model == Menu:
            return qs.filter(organization=org)
        elif self.model == ProductCategory:
            return qs.filter(menu__organization=org)
        elif self.model == Product:
            return qs.filter(organization=org)
        elif any(f.name == 'organization' for f in self.model._meta.fields):
            return qs.filter(organization=org)
        elif any(f.name == 'menu' for f in self.model._meta.fields):
            return qs.filter(menu__organization=org)
        elif any(f.name == 'product' for f in self.model._meta.fields):
            # For Modifier, StopList etc if they link to product
            return qs.filter(product__organization=org)
            
    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        if request.user.is_superuser:
            return filters
        # Remove organization/menu filters as they are filtered by queryset
        restricted = ['organization', 'menu', 'menu__organization']
        return [f for f in filters if f not in restricted]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                # Limit choices to user's organization for relevant fields
                if db_field.name == 'organization':
                    kwargs["queryset"] = db_field.related_model.objects.filter(org_id=org.org_id)
                elif db_field.name == 'menu':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
                elif db_field.name == 'category': # For Product.category
                    kwargs["queryset"] = db_field.related_model.objects.filter(menu__organization=org)
                elif db_field.name == 'product': # For Modifier.product etc
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
                elif db_field.name == 'parent': # For ProductCategory.parent
                    kwargs["queryset"] = db_field.related_model.objects.filter(menu__organization=org)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if hasattr(obj, 'organization'):
                    obj.organization = org
                # For models related to menu
                if hasattr(obj, 'menu') and not obj.menu_id:
                     # Attempt to find a menu for this organization if not set
                     pass 
        super().save_model(request, obj, form, change)

    def lookup_allowed(self, lookup, value):
        # Разрешаем фильтрацию по UUID первичным ключам, даже если Django считает их слишком глубокими
        if lookup.endswith('__org_id__exact') or lookup.endswith('__menu_id__exact') or \
           lookup.endswith('__product_id__exact') or lookup.endswith('__subgroup_id__exact'):
            return True
        return super().lookup_allowed(lookup, value)

@admin.register(Menu)
class MenuAdmin(BaseProductAdmin):
    list_display = ('menu_name', 'organization', 'created_at')
    list_filter = (('organization', admin.RelatedOnlyFieldListFilter), 'is_active')
    search_fields = ('menu_name',)

@admin.register(ProductCategory)
class ProductCategoryAdmin(BaseProductAdmin):
    list_display = ('subgroup_name', 'subgroup_id', 'parent', 'order_index', 'menu')
    list_filter = (
        ('menu__organization', admin.RelatedOnlyFieldListFilter),
        ('menu', admin.RelatedOnlyFieldListFilter),
        'parent'
    )
    search_fields = ('subgroup_name', 'subgroup_id')
    readonly_fields = ('outer_data',)

@admin.register(Product)
class ProductAdmin(BaseProductAdmin):
    list_display = ('product_name', 'price', 'category', 'type', 'is_available', 'has_modifiers')
    list_filter = (
        ('organization', admin.RelatedOnlyFieldListFilter),
        ('menu', admin.RelatedOnlyFieldListFilter),
        ('category', admin.RelatedOnlyFieldListFilter),
        'is_available',
        'type'
    )
    search_fields = ('product_name', 'product_id', 'product_code')
    readonly_fields = ('outer_data', 'image_url')

@admin.register(Modifier)
class ModifierAdmin(BaseProductAdmin):
    list_display = ('modifier_name', 'price', 'product', 'is_required')
    list_filter = (
        ('product__organization', admin.RelatedOnlyFieldListFilter),
        ('product__menu', admin.RelatedOnlyFieldListFilter),
        'is_required'
    )
    search_fields = ('modifier_name',)

@admin.register(StopList)
class StopListAdmin(BaseProductAdmin):
    list_display = ('product', 'organization', 'reason', 'is_auto_added', 'created_at')
    list_filter = (('organization', admin.RelatedOnlyFieldListFilter), 'is_auto_added')
    search_fields = ('product__product_name', 'reason')

@admin.register(FastMenuGroup)
class FastMenuGroupAdmin(BaseProductAdmin):
    list_display = ('name', 'organization', 'is_active', 'order', 'created_at')
    list_filter = (('organization', admin.RelatedOnlyFieldListFilter), 'is_active')
    search_fields = ('name',)
    ordering = ('order', 'name')

@admin.register(FastMenuItem)
class FastMenuItemAdmin(BaseProductAdmin):
    list_display = ('group', 'product', 'order')
    list_filter = (
        ('group__organization', admin.RelatedOnlyFieldListFilter),
        ('group', admin.RelatedOnlyFieldListFilter),
        ('product__organization', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('group__name', 'product__product_name')
    ordering = ('group', 'order')
