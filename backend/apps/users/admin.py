from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, DeliveryAddress, BotSyncToken
from .forms import CustomUserChangeForm
from apps.organizations.models import Organization

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'description')

class OrgRestrictedMixin:
    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        org = getattr(request.user, 'organization', None)
        if not org:
            return qs.none()
        if self.model == User:
            return qs.filter(organization=org)
        if any(f.name == 'organization' for f in self.model._meta.fields):
            return qs.filter(organization=org)
        if any(f.name == 'user' for f in self.model._meta.fields):
            return qs.filter(user__organization=org)
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
                elif db_field.name == 'street':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
                elif db_field.name == 'user':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organization=org)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if db_field.name == 'terminals':
                    kwargs["queryset"] = db_field.related_model.objects.filter(organizations=org)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if hasattr(obj, 'organization'):
                    obj.organization = org
                elif self.model == User:
                    obj.organization = org
        super().save_model(request, obj, form, change)

class DeliveryAddressInline(admin.TabularInline):
    model = DeliveryAddress
    extra = 0
    fields = ('city_name', 'street_name', 'house', 'flat', 'entrance', 'floor', 'latitude', 'longitude', 'comment', 'is_default')

@admin.register(User)
class CustomUserAdmin(OrgRestrictedMixin, UserAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'full_name', 'telegram_id', 'phone', 'is_bot_subscribed', 'role', 'organization', 'is_active', 'is_staff')
    list_filter = ('role', 'organization', 'is_bot_subscribed', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    inlines = [DeliveryAddressInline]
    
    filter_horizontal = ('terminals',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Сброс пароля', {'fields': ('new_password',)}),
        ('Дополнительная информация', {'fields': ('role', 'organization', 'phone', 'telegram_id', 'telegram_username', 'terminals', 'is_bot_subscribed', 'chat_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'organization', 'phone')}),
    )

    def save_model(self, request, obj, form, change):
        if 'new_password' in form.cleaned_data and form.cleaned_data['new_password']:
            obj.set_password(form.cleaned_data['new_password'])
        super().save_model(request, obj, form, change)

@admin.register(BotSyncToken)
class BotSyncTokenAdmin(admin.ModelAdmin):
    list_display = ('bot_sync_uuid', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('bot_sync_uuid', 'user__username')
    readonly_fields = ('bot_sync_uuid', 'created_at')


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(OrgRestrictedMixin, admin.ModelAdmin):
    list_display = ('user', 'city_name', 'street_name', 'house', 'flat', 'is_default')
    list_filter = ('is_default', 'city_name')
    search_fields = ('user__username', 'city_name', 'street_name')
