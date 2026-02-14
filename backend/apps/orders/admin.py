from django.contrib import admin
from .models import Order, OrderItem, OrderItemModifier, IikoRequestLog
from apps.organizations.models import Organization

class OrderBaseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        org = getattr(request.user, 'organization', None)
        if not org:
            return qs.none()
        
        if hasattr(self.model, 'organization'):
            return qs.filter(organization=org)
        elif hasattr(self.model, 'order'):
            return qs.filter(order__organization=org)
        elif hasattr(self.model, 'order_item'):
            return qs.filter(order_item__order__organization=org)
        return qs

    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        if request.user.is_superuser:
            return filters
        return [f for f in filters if f not in ['organization', 'organizations']]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if db_field.name == 'organization':
                    kwargs["queryset"] = Organization.objects.filter(org_id=org.org_id)
                elif db_field.name == 'order':
                    kwargs["queryset"] = Order.objects.filter(organization=org)
                elif db_field.name == 'payment_type':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
                elif db_field.name == 'terminal':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if hasattr(obj, 'organization'):
                    obj.organization = org
        super().save_model(request, obj, form, change)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price', 'total_price')


class IikoRequestLogInline(admin.TabularInline):
    model = IikoRequestLog
    extra = 0
    readonly_fields = ('payload', 'success', 'created_at')
    can_delete = False
    max_num = 10
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(OrderBaseAdmin):
    list_display = ('order_number', 'organization', 'user', 'total_amount', 'delivery_cost', 'status', 'created_at')
    list_filter = ('status', 'organization', 'created_at')
    search_fields = ('order_number', 'phone', 'user__username')
    inlines = [OrderItemInline, IikoRequestLogInline]
    readonly_fields = ('order_id', 'iiko_order_id', 'iiko_response', 'error_message', 'sent_to_iiko_at')

@admin.register(OrderItem)
class OrderItemAdmin(OrderBaseAdmin):
    list_display = ('order', 'product_name', 'quantity', 'price', 'total_price')
    list_filter = ('order__organization', 'created_at')

@admin.register(OrderItemModifier)
class OrderItemModifierAdmin(OrderBaseAdmin):
    list_display = ('order_item', 'modifier_name', 'quantity', 'price')


@admin.register(IikoRequestLog)
class IikoRequestLogAdmin(OrderBaseAdmin):
    list_display = ('order', 'success', 'created_at')
    list_filter = ('success', 'created_at')
    readonly_fields = ('order', 'payload', 'success', 'created_at')
    search_fields = ('order__order_number',)
