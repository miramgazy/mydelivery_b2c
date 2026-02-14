import json
import logging
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Organization, Terminal, PaymentType, Street, City, Discount

logger = logging.getLogger(__name__)

# Шаблон базовой структуры запроса iikoCloud (генерируется кодом)
IIKO_BASE_STRUCTURE_TEMPLATE = {
    "organizationId": "<uuid организации>",
    "terminalGroupId": "<uuid терминала>",
    "order": {
        "orderServiceType": "DeliveryByCourier | DeliveryByClient",
        "status": "Unconfirmed",
        "customer": {"name": "...", "phone": "+7..."},
        "phone": "+7...",
        "deliveryPoint": {
            "address": {"city": "...", "street": {"name": "..."}, "house": "...", "flat": "..."},
            "или type": "coordinates",
            "coordinates": {"latitude": 0, "longitude": 0}
        },
        "items": [{"type": "Product", "productId": "...", "amount": 1, "price": 0, "modifiers": [{"productId": "...", "amount": 1}]}],
        "customerPayments": [{"paymentTypeId": "...", "sum": 0}],
        "comment": "..."
    }
}


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для админки с фильтрацией по организации"""
    def get_queryset(self, request):
        self.request = request  # Сохраняем запрос для использования в методах
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        org = getattr(request.user, 'organization', None)
        if not org:
            return qs.none()
            
        if self.model == Organization:
            return qs.filter(org_id=org.org_id)
        
        if self.model == Terminal:
            return qs.filter(organization=org)

        # Проверка наличия поля organization (FK)
        if any(f.name == 'organization' for f in self.model._meta.fields):
            return qs.filter(organization=org)
            
        # Проверка ManyToMany связи (через related_name или прямое поле)
        if hasattr(self.model, 'organizations'):
             return qs.filter(organizations=org)
            
        return qs

    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        if request.user.is_superuser:
            return filters
        # Список фильтров, которые могут быть чувствительными или избыточными для админа организации
        restricted = ['organization', 'organizations', 'organizations__org_name']
        return [f for f in filters if f not in restricted]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org and db_field.name == 'organization':
                kwargs["queryset"] = Organization.objects.filter(org_id=org.org_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if db_field.name == 'terminals':
                    kwargs["queryset"] = Terminal.objects.filter(organization=org)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                if hasattr(obj, 'organization'):
                    obj.organization = org
        super().save_model(request, obj, form, change)

@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ('org_name', 'iiko_organization_id', 'city', 'get_terminals_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'city')
    change_form_template = 'admin/organizations/organization/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('org_name', 'api_key', 'iiko_organization_id', 'city', 'phone', 'address')
        }),
        ('Telegram Bot', {
            'fields': ('bot_token', 'bot_username'),
            'classes': ('collapse',)
        }),
        ('iiko API — конструктор запроса', {
            'fields': ('iiko_base_structure_display', 'api_custom_params'),
            'description': (
                'Конструктор запроса iikoCloud: базовая структура (генерируется кодом) '
                'дополняется параметрами из блока ниже. Поле items защищено — блюда формируются системой.'
            )
        }),
        ('Оформление', {
            'fields': ('primary_color',)
        }),
        (None, {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'iiko_base_structure_display')

    def iiko_base_structure_display(self, obj):
        """Блок «Базовая структура (Только чтение)» — шаблон JSON, генерируемого кодом."""
        if obj is None:
            return "(Сохранение организации для просмотра)"
        text = json.dumps(IIKO_BASE_STRUCTURE_TEMPLATE, ensure_ascii=False, indent=2)
        return mark_safe(f'<pre style="background:#f8f9fa;padding:12px;border-radius:4px;overflow:auto;">{text}</pre>')
    iiko_base_structure_display.short_description = 'Базовая структура (Только чтение)'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'api_custom_params':
            kwargs['widget'] = admin.widgets.AdminTextareaWidget(attrs={
                'placeholder': '{"order": {"comment": "Срочно"}, "createOrderSettings": {"servicePrint": true}}',
                'rows': 10,
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_terminals_count(self, obj):
        return obj.terminals.count()
    get_terminals_count.short_description = 'Терминалов'
    search_fields = ('org_name', 'org_id', 'iiko_organization_id')
    actions = ['import_menu_from_iiko']

    @admin.action(description='Загрузить меню из iikoCloud')
    def import_menu_from_iiko(self, request, queryset):
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import MenuSyncService
        from django.contrib import messages
        
        updated_count = 0
        errors = []

        for org in queryset:
            if not org.api_key or not org.iiko_organization_id:
                errors.append(f"{org.org_name}: Нет API Key или ID организации")
                continue
            
            try:
                client = IikoClient(org.api_key)
                client.authenticate()
                menu_data = client.get_menu(org.iiko_organization_id)
                
                service = MenuSyncService()
                service.sync_menu(org, menu_data)
                updated_count += 1
            except Exception as e:
                errors.append(f"{org.org_name}: {str(e)}")

        if updated_count > 0:
            self.message_user(request, f"Меню успешно обновлено для {updated_count} организаций.", messages.SUCCESS)
        
        if errors:
            self.message_user(request, "Ошибки: " + "; ".join(errors), messages.ERROR)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:object_id>/import_menu/', self.admin_site.admin_view(self.import_menu_view), name='organization_import_menu'),
            path('<uuid:object_id>/import_external_menu/', self.admin_site.admin_view(self.import_external_menu_view), name='organization_import_external_menu'),
        ]
        return custom_urls + urls

    def import_menu_view(self, request, object_id):
        from django.shortcuts import get_object_or_404, redirect, render
        from django.contrib import messages
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import MenuSyncService

        org = get_object_or_404(Organization, pk=object_id)
        
        if not org.api_key or not org.iiko_organization_id:
            self.message_user(request, "Ошибка: Нет API Key или ID организации", messages.ERROR)
            return redirect('admin:organizations_organization_change', object_id)

        try:
            # 1. Fetch entire menu from iiko
            client = IikoClient(org.api_key)
            client.authenticate()
            menu_data = client.get_menu(org.iiko_organization_id)
            all_groups = menu_data.get('groups', [])
            
            # 2. Identify Root Groups (parentGroup is None) and filter by child count
            # Count children for each group
            children_counts = {}
            for g in all_groups:
                p_id = g.get('parentGroup')
                if p_id:
                    children_counts[p_id] = children_counts.get(p_id, 0) + 1
            
            # Filter roots: Must be parentless AND have >= 5 direct children
            root_groups = []
            for g in all_groups:
                if not g.get('parentGroup'):
                    child_count = children_counts.get(g['id'], 0)
                    if child_count >= 5:
                        root_groups.append(g)
            
            # Handle POST: User selected groups
            if request.method == 'POST':
                selected_ids = request.POST.getlist('selected_groups')
                if not selected_ids:
                    self.message_user(request, "Не выбрано ни одной группы.", messages.WARNING)
                    return redirect('admin:organization_import_menu', object_id=object_id)
                
                # Sync logic with selected roots
                service = MenuSyncService()
                service.sync_selected_roots(org, menu_data, selected_ids)
                
                self.message_user(request, f"Меню успешно обновлено из {len(selected_ids)} групп.", messages.SUCCESS)
                return redirect('admin:organizations_organization_change', object_id)
            
            # Handle GET: Show selection form
            context = { # Standard Admin context
                **self.admin_site.each_context(request),
                'opts': self.model._meta,
                'object': org,
                'groups': root_groups,
                'title': 'Импорт меню из iiko'
            }
            return render(request, 'admin/organizations/organization/select_menu_groups.html', context)

        except Exception as e:
            self.message_user(request, f"Ошибка загрузки: {str(e)}", messages.ERROR)
            return redirect('admin:organizations_organization_change', object_id)

    def import_external_menu_view(self, request, object_id):
        from django.shortcuts import get_object_or_404, redirect, render
        from django.contrib import messages
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import MenuSyncService

        org = get_object_or_404(Organization, pk=object_id)
        
        if not org.api_key or not org.iiko_organization_id:
            self.message_user(request, "Ошибка: Нет API Key или ID организации", messages.ERROR)
            return redirect('admin:organizations_organization_change', object_id)

        try:
            client = IikoClient(org.api_key)
            client.authenticate()
            
            # Debug organizations
            orgs_info = client.get_organizations()
            logger.info(f"Available organizations for key: {orgs_info}")
            logger.info(f"Current organization iiko_organization_id: {org.iiko_organization_id}")

            # Handle POST: User selected a menu
            if request.method == 'POST':
                selected_menu_id = request.POST.get('selected_menu')
                if not selected_menu_id:
                    self.message_user(request, "Не выбрано меню.", messages.WARNING)
                    return redirect('admin:organization_import_external_menu', object_id=object_id)
                
                # Fetch detailed menu content
                menu_details = client.get_external_menu_by_id([org.iiko_organization_id], selected_menu_id)
                
                # Sync logic
                service = MenuSyncService()
                service.sync_external_menu(org, menu_details)
                
                self.message_user(request, f"Внешнее меню успешно загружено.", messages.SUCCESS)
                return redirect('admin:organizations_organization_change', object_id)
            
            # Handle GET: Show available external menus
            # 1. Try to get menus for current org
            menus_response = client.get_external_menus([org.iiko_organization_id])
            logger.info(f"Iiko external menus response for {org.org_name}: {menus_response}")
            
            external_menus = menus_response.get('externalMenus', [])
            
            # 2. If empty, try all available orgs (maybe it's on a parent/sibling)
            if not external_menus:
                all_orgs_data = client.get_organizations()
                all_org_ids = [o['id'] for o in all_orgs_data.get('organizations', [])]
                if all_org_ids:
                    logger.info(f"Specific org menu list is empty, trying all avail IDs: {all_org_ids}")
                    all_menus_response = client.get_external_menus(all_org_ids)
                    external_menus = all_menus_response.get('externalMenus', [])
                    logger.info(f"Total menus found for all orgs: {len(external_menus)}")
                
                if not external_menus:
                    self.message_user(
                        request, 
                        f"Внешние меню не найдены. ID организации: {org.iiko_organization_id}. "
                        f"Доступные организации для ключа: {[o.get('name') for o in all_orgs_data.get('organizations', [])]}",
                        messages.WARNING
                    )
            
            context = {
                **self.admin_site.each_context(request),
                'opts': self.model._meta,
                'object': org,
                'external_menus': external_menus,
                'title': 'Загрузить внешнее меню из iiko'
            }
            return render(request, 'admin/organizations/organization/select_external_menu.html', context)

        except Exception as e:
            self.message_user(request, f"Ошибка загрузки внешнего меню: {str(e)}", messages.ERROR)
            return redirect('admin:organizations_organization_change', object_id)

@admin.register(Terminal)
class TerminalAdmin(BaseAdmin):
    list_display = ('terminal_group_name', 'organization', 'city', 'iiko_organization_id', 'is_active')
    list_filter = ('is_active', 'organization', 'city')
    search_fields = ('terminal_group_name', 'terminal_id', 'iiko_organization_id')
    change_list_template = "admin/organizations/terminal_changelist.html"

    # Removed get_organizations as it's now a direct ForeignKey 'organization'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('sync-iiko/', self.admin_site.admin_view(self.sync_iiko_view), name='terminal_sync_iiko'),
        ]
        return custom_urls + urls

    def sync_iiko_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import TerminalSyncService
        
        if request.method == 'POST':
            org_id = request.POST.get('organization_id')
            if not org_id:
                self.message_user(request, "Выберите организацию", messages.WARNING)
                return redirect('admin:terminal_sync_iiko')
            
            try:
                org = Organization.objects.get(pk=org_id)
                if not org.api_key or not org.iiko_organization_id:
                    self.message_user(request, f"Организация {org.org_name} не имеет API Key или iiko ID", messages.ERROR)
                    return redirect('admin:terminal_sync_iiko')

                client = IikoClient(org.api_key)
                # No need to authenticate explicitly, get_headers handles it
                data = client.get_terminal_groups([org.iiko_organization_id])
                
                service = TerminalSyncService()
                synced = service.sync_terminal_groups(data, organization=org)
                
                self.message_user(request, f"Успешно синхронизировано {len(synced)} терминалов для {org.org_name}", messages.SUCCESS)
                return redirect('admin:organizations_terminal_changelist')
            except Exception as e:
                self.message_user(request, f"Ошибка при синхронизации: {str(e)}", messages.ERROR)
                return redirect('admin:terminal_sync_iiko')

        organizations = Organization.objects.filter(is_active=True)
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                organizations = organizations.filter(org_id=org.org_id)
            else:
                organizations = organizations.none()
        context = {
            **self.admin_site.each_context(request),
            'organizations': organizations,
            'title': 'Запрос списка терминалов из iiko'
        }
        return render(request, 'admin/organizations/sync_terminals.html', context)

@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ('name', 'organization', 'city_id', 'iiko_city_id', 'is_active')
    list_filter = ('organization', 'is_active')
    search_fields = ('name', 'city_id')
    readonly_fields = ('city_id', 'created_at', 'updated_at')
    
    def get_fields(self, request, obj=None):
        fields = ['name', 'organization', 'iiko_city_id', 'is_active']
        if obj:  # При редактировании показываем city_id как read-only
            fields.insert(0, 'city_id')
        fields.extend(['created_at', 'updated_at'])
        return fields

@admin.register(PaymentType)
class PaymentTypeAdmin(BaseAdmin):
    list_display = ('payment_name', 'payment_type', 'organization', 'is_active')
    list_filter = ('organization', 'is_active')
    search_fields = ('payment_name',)
    change_list_template = "admin/organizations/paymenttype_changelist.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('sync-payment-types/', self.admin_site.admin_view(self.sync_payment_types_view), name='paymenttype_sync_iiko'),
        ]
        return custom_urls + urls

    def sync_payment_types_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import MenuSyncService
        
        if request.method == 'POST':
            org_id = request.POST.get('organization_id')
            if not org_id:
                self.message_user(request, "Выберите организацию", messages.WARNING)
                return redirect('admin:paymenttype_sync_iiko')
            
            try:
                org = Organization.objects.get(pk=org_id)
                if not org.api_key or not org.iiko_organization_id:
                    self.message_user(request, f"Организация {org.org_name} не имеет API Key или iiko ID", messages.ERROR)
                    return redirect('admin:paymenttype_sync_iiko')

                client = IikoClient(org.api_key)
                client.authenticate()
                data = client.get_payment_types([org.iiko_organization_id])
                
                service = MenuSyncService()
                synced = service.sync_payment_types(org, data)
                
                self.message_user(request, f"Успешно синхронизировано {len(synced)} типов оплаты для {org.org_name}", messages.SUCCESS)
                return redirect('admin:organizations_paymenttype_changelist')
            except Exception as e:
                self.message_user(request, f"Ошибка при синхронизации: {str(e)}", messages.ERROR)
                return redirect('admin:paymenttype_sync_iiko')

        organizations = Organization.objects.filter(is_active=True)
        if not request.user.is_superuser:
            org = getattr(request.user, 'organization', None)
            if org:
                organizations = organizations.filter(org_id=org.org_id)
            else:
                organizations = organizations.none()
        context = {
            **self.admin_site.each_context(request),
            'organizations': organizations,
            'title': 'Загрузка типов оплаты из iiko'
        }
        return render(request, 'admin/organizations/sync_payment_types.html', context)


@admin.register(Discount)
class DiscountAdmin(BaseAdmin):
    list_display = ('name', 'organization', 'percent', 'mode', 'is_active', 'is_deleted_in_iiko', 'updated_at')
    list_filter = ('is_active', 'organization', 'mode')
    search_fields = ('name',)
    readonly_fields = ('external_id', 'updated_at')


@admin.register(Street)
class StreetAdmin(BaseAdmin):
    list_display = ('street_name', 'city', 'organization', 'is_deleted')
    list_filter = ('organization', 'city', 'is_deleted')
    search_fields = ('street_name',)
