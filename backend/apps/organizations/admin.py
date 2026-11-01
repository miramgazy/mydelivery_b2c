import json
import logging
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import Organization, RmsBase, Terminal, PaymentType, Street, City, Discount

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

class RmsBaseInline(admin.TabularInline):
    model = RmsBase
    extra = 1
    fields = ('name', 'iiko_organization_id', 'address', 'phone', 'is_active', 'order_index', 'terminals_link')
    readonly_fields = ('terminals_link',)

    def terminals_link(self, obj):
        if obj and obj.pk:
            count = obj.terminals.count()
            changelist_url = reverse('admin:organizations_terminal_changelist') + f'?rms_base__id__exact={obj.pk}'
            sync_url = reverse('admin:rms_sync_terminals', args=[obj.pk])
            return mark_safe(
                f'<a href="{changelist_url}"><strong>{count}</strong> терминалов</a> &nbsp;|&nbsp; '
                f'<a class="button" href="{sync_url}" style="padding:2px 8px;font-size:11px;">Выгрузить терминалы</a>'
            )
        return '—'
    terminals_link.short_description = 'Терминалы'


@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ('org_id', 'org_name', 'iiko_api_version', 'iiko_chain_id', 'iiko_organization_id', 'city', 'get_rms_bases_count', 'get_terminals_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'iiko_api_version', 'city')
    change_form_template = 'admin/organizations/organization/change_form.html'
    inlines = [RmsBaseInline]
    fieldsets = (
        ('Основные настройки сети / проекта', {
            'fields': ('org_id_display', 'org_name', 'iiko_api_version', 'api_key', 'iiko_app_id', 'iiko_client_secret', 'iiko_chain_id', 'iiko_organization_id', 'city', 'phone', 'address')
        }),
        ('Telegram Bot', {
            'fields': ('bot_token', 'bot_username', 'tma_name'),
            'classes': ('collapse',)
        }),
        ('iiko API — конструктор запроса', {
            'fields': ('iiko_base_structure_display', 'api_custom_params'),
            'description': (
                'Конструктор запроса iikoCloud: базовая структура (генерируется кодом) '
                'дополняется параметрами из блока ниже. Поле items защищено — блюда формируются системой.'
            )
        }),
        ('Интеграции и оформление', {
            'fields': ('yandex_maps_api_key', 'primary_color', 'webhook_link'),
            'classes': ('collapse',)
        }),
        (None, {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('org_id_display', 'created_at', 'updated_at', 'iiko_base_structure_display')

    def org_id_display(self, obj):
        """ID организации (для URL веб-сайта: ?org=...)"""
        if obj:
            return mark_safe(f'<strong style="font-family:monospace;font-size:14px;">{obj.org_id}</strong>')
        return '—'
    org_id_display.short_description = 'ID организации'

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

    def get_rms_bases_count(self, obj):
        return obj.rms_bases.count()
    get_rms_bases_count.short_description = 'RMS баз'

    def get_terminals_count(self, obj):
        return obj.terminals.count()
    get_terminals_count.short_description = 'Терминалов'
    search_fields = ('org_name', 'org_id', 'iiko_chain_id', 'iiko_organization_id')
    actions = ['import_rms_bases_from_iiko', 'import_menu_from_iiko', 'set_telegram_webhook', 'check_telegram_webhook']

    @admin.action(description='Установить Telegram Webhook (BACKEND_URL)')
    def set_telegram_webhook(self, request, queryset):
        import requests
        from django.conf import settings
        backend_url = getattr(settings, 'BACKEND_URL', '').rstrip('/')
        if not backend_url:
            self.message_user(request, "В настройках сервера не задан BACKEND_URL", messages.ERROR)
            return

        for org in queryset:
            if not org.bot_token:
                self.message_user(request, f"{org.org_name}: Не указан bot_token", messages.WARNING)
                continue
            webhook_url = f"{backend_url}/api/telegram/webhook/{org.bot_token}/"
            api_url = f"https://api.telegram.org/bot{org.bot_token}/setWebhook"
            try:
                res = requests.post(api_url, data={'url': webhook_url}, timeout=10).json()
                if res.get('ok'):
                    self.message_user(request, f"{org.org_name}: Webhook успешно установлен на {webhook_url}", messages.SUCCESS)
                else:
                    self.message_user(request, f"{org.org_name}: Ошибка Telegram: {res.get('description')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"{org.org_name}: Ошибка сети: {e}", messages.ERROR)

    @admin.action(description='Проверить статус Telegram Webhook')
    def check_telegram_webhook(self, request, queryset):
        import requests
        for org in queryset:
            if not org.bot_token:
                self.message_user(request, f"{org.org_name}: Не указан bot_token", messages.WARNING)
                continue
            api_url = f"https://api.telegram.org/bot{org.bot_token}/getWebhookInfo"
            try:
                res = requests.get(api_url, timeout=10).json()
                if res.get('ok'):
                    result = res.get('result', {})
                    url = result.get('url') or '(не установлен)'
                    pending = result.get('pending_update_count', 0)
                    last_err = result.get('last_error_message')
                    msg = f"{org.org_name}: URL={url}, в очереди={pending}"
                    if last_err:
                        msg += f", Последняя ошибка Telegram: {last_err}"
                    self.message_user(request, msg, messages.INFO)
                else:
                    self.message_user(request, f"{org.org_name}: Ошибка: {res.get('description')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"{org.org_name}: Ошибка сети: {e}", messages.ERROR)

    @admin.action(description='Загрузить список RMS баз из iikoCloud')
    def import_rms_bases_from_iiko(self, request, queryset):
        from apps.iiko_integration.client import IikoClient
        
        for org in queryset:
            if not org.api_key:
                self.message_user(request, f"{org.org_name}: Нет API Key", messages.ERROR)
                continue
            try:
                client = IikoClient(org.api_key)
                res = client.get_organizations(return_additional_info=True)
                orgs_list = res.get('organizations', [])
                if not orgs_list:
                    self.message_user(request, f"{org.org_name}: iiko вернул пустой список организаций", messages.WARNING)
                    continue
                
                created_count = 0
                updated_count = 0
                for item in orgs_list:
                    item_id = str(item.get('id'))
                    item_name = item.get('name') or f"Филиал {item_id[:8]}"
                    # Если этот ID совпадает с chain_id, пропускаем создание отдельной RMS
                    if org.iiko_chain_id and item_id.lower() == str(org.iiko_chain_id).strip().lower():
                        continue
                    
                    rms, created = RmsBase.objects.update_or_create(
                        organization=org,
                        iiko_organization_id=item_id,
                        defaults={
                            'name': item_name,
                            'is_active': not item.get('isDeleted', False),
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                self.message_user(
                    request,
                    f"Успешно обработаны RMS базы для {org.org_name}: добавлено {created_count}, обновлено {updated_count}",
                    messages.SUCCESS
                )
            except Exception as e:
                self.message_user(request, f"Ошибка при загрузке RMS баз для {org.org_name}: {str(e)}", messages.ERROR)

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

@admin.register(RmsBase)
class RmsBaseAdmin(BaseAdmin):
    list_display = ('name', 'organization', 'iiko_organization_id', 'terminals_count', 'is_active', 'order_index', 'created_at')
    list_filter = ('organization', 'is_active')
    search_fields = ('name', 'iiko_organization_id', 'address')
    actions = ['sync_terminals_for_rms']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:rms_id>/sync-terminals/', self.admin_site.admin_view(self.sync_single_rms_view), name='rms_sync_terminals'),
        ]
        return custom_urls + urls

    def terminals_count(self, obj):
        count = obj.terminals.count()
        changelist_url = reverse('admin:organizations_terminal_changelist') + f'?rms_base__id__exact={obj.pk}'
        return mark_safe(f'<a href="{changelist_url}"><strong>{count}</strong> терминалов</a>')
    terminals_count.short_description = 'Терминалы'

    def sync_single_rms_view(self, request, rms_id):
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import TerminalSyncService
        rms = get_object_or_404(RmsBase, pk=rms_id)
        org = rms.organization
        if not org or not org.api_key:
            self.message_user(request, "У организации не настроен API Key iiko", messages.ERROR)
            return redirect('admin:organizations_rmsbase_changelist')
        try:
            client = IikoClient(org.api_key)
            data = client.get_terminal_groups([rms.iiko_organization_id])
            service = TerminalSyncService()
            synced = service.sync_terminal_groups(data, organization=org, rms_base=rms)
            self.message_user(request, f"Успешно выгружено {len(synced)} терминалов для RMS «{rms.name}»", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка выгрузки терминалов для «{rms.name}»: {str(e)}", messages.ERROR)
        return redirect('admin:organizations_terminal_changelist')

    @admin.action(description='Выгрузить терминалы по отдельности для выбранных RMS баз')
    def sync_terminals_for_rms(self, request, queryset):
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import TerminalSyncService
        total = 0
        service = TerminalSyncService()
        for rms in queryset:
            org = rms.organization
            if not org or not org.api_key:
                continue
            try:
                client = IikoClient(org.api_key)
                data = client.get_terminal_groups([rms.iiko_organization_id])
                synced = service.sync_terminal_groups(data, organization=org, rms_base=rms)
                total += len(synced)
            except Exception as e:
                self.message_user(request, f"Ошибка выгрузки для {rms.name}: {e}", messages.ERROR)
        self.message_user(request, f"Успешно выгружено {total} терминалов для выбранных RMS баз", messages.SUCCESS)


@admin.register(Terminal)
class TerminalAdmin(BaseAdmin):
    list_display = ('terminal_group_name', 'organization', 'rms_base', 'city', 'iiko_organization_id', 'is_active')
    list_filter = ('is_active', 'organization', 'rms_base', 'city')
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
        from apps.iiko_integration.client import IikoClient
        from apps.iiko_integration.services import TerminalSyncService
        
        if request.method == 'POST':
            org_id = request.POST.get('organization_id')
            rms_base_id = request.POST.get('rms_base_id')
            if not org_id:
                self.message_user(request, "Выберите организацию", messages.WARNING)
                return redirect('admin:terminal_sync_iiko')
            
            try:
                org = Organization.objects.get(pk=org_id)
                if not org.api_key:
                    self.message_user(request, f"Организация {org.org_name} не имеет API Key", messages.ERROR)
                    return redirect('admin:terminal_sync_iiko')

                client = IikoClient(org.api_key)
                service = TerminalSyncService()

                if rms_base_id and rms_base_id != 'all':
                    rms_base = get_object_or_404(RmsBase, pk=rms_base_id, organization=org)
                    data = client.get_terminal_groups([rms_base.iiko_organization_id])
                    synced = service.sync_terminal_groups(data, organization=org, rms_base=rms_base)
                    self.message_user(request, f"Успешно выгружено {len(synced)} терминалов для RMS «{rms_base.name}»", messages.SUCCESS)
                else:
                    # Выгружаем для всех активных RMS баз чейна по отдельности
                    active_rms = list(org.rms_bases.filter(is_active=True))
                    if active_rms:
                        total_synced = 0
                        for rms in active_rms:
                            try:
                                data = client.get_terminal_groups([rms.iiko_organization_id])
                                synced = service.sync_terminal_groups(data, organization=org, rms_base=rms)
                                total_synced += len(synced)
                            except Exception as e:
                                self.message_user(request, f"Ошибка выгрузки для RMS «{rms.name}»: {e}", messages.WARNING)
                        self.message_user(request, f"Успешно выгружено {total_synced} терминалов для {len(active_rms)} RMS баз чейна {org.org_name}", messages.SUCCESS)
                    elif org.iiko_organization_id:
                        data = client.get_terminal_groups([org.iiko_organization_id])
                        synced = service.sync_terminal_groups(data, organization=org)
                        self.message_user(request, f"Успешно выгружено {len(synced)} терминалов для {org.org_name}", messages.SUCCESS)
                    else:
                        self.message_user(request, f"У организации {org.org_name} не настроены RMS базы и отсутствует iiko_organization_id", messages.ERROR)
                        return redirect('admin:terminal_sync_iiko')

                return redirect('admin:organizations_terminal_changelist')
            except Exception as e:
                self.message_user(request, f"Ошибка при синхронизации: {str(e)}", messages.ERROR)
                return redirect('admin:terminal_sync_iiko')

        organizations = Organization.objects.filter(is_active=True).prefetch_related('rms_bases')
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
