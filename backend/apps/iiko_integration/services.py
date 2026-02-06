import logging
import uuid
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from apps.products.models import Menu, ProductCategory, Product, Modifier, StopList
from apps.organizations.models import Organization, Terminal
from apps.iiko_integration.client import IikoClient, IikoAPIException

logger = logging.getLogger(__name__)

class MenuSyncService:
    def sync_menu(self, organization: Organization, menu_data: Dict[str, Any]):
        """
        Syncs menu data from iiko to local database.
        """
        if not menu_data:
            logger.warning("No menu data provided for sync")
            return

        with transaction.atomic():
            # 1. Ensure a default Menu exists for the organization
            menu, _ = Menu.objects.get_or_create(
                organization=organization,
                defaults={'menu_name': f"Меню {organization.org_name}"}
            )

            # 2. Process Groups (Categories) - но только те, которые не являются группами модификаторов
            groups = menu_data.get('groups', [])
            products = menu_data.get('products', [])
            # Map for quick lookup of modifier names
            products_map = {p['id']: p for p in products}
            
            # Передаем products для проверки, чтобы не создавать категории из групп модификаторов
            self._sync_categories(menu, groups, products)
            
            # 3. Process Products & Modifiers
            self._sync_products_and_modifiers(menu, organization, products, products_map)

    def _sync_categories(self, menu: Menu, groups: List[Dict], products: List[Dict] = None):
        """
        Синхронизация категорий из групп iiko.
        Исключает группы модификаторов - создает категории только для групп, в которых есть продукты.
        
        Args:
            menu: Меню для привязки категорий
            groups: Список групп из iiko API
            products: Список продуктов из iiko API (для проверки, используется ли группа)
        """
        if products is None:
            products = []
        
        # Создаем множество ID групп, которые используются продуктами
        # Группа используется, если у продукта groupId или parentGroup равен ID группы
        used_group_ids = set()
        for product in products:
            if product.get('isDeleted'):
                continue
            group_id = product.get('groupId')
            parent_group_id = product.get('parentGroup')
            if group_id:
                used_group_ids.add(str(group_id))
            if parent_group_id:
                used_group_ids.add(str(parent_group_id))
        
        # 1. Create/Update only groups that are used by products (not modifier groups)
        for group in groups:
            if group.get('isDeleted'):
                continue
            
            group_id = str(group['id'])
            
            # Пропускаем группы модификаторов - они не используются как категории продуктов
            # Группа модификаторов определяется как группа, в которой нет продуктов
            if group_id not in used_group_ids:
                logger.debug(f"Skipping modifier group (no products): {group.get('name')} (ID: {group_id})")
                continue

            Category_id = group['id']
            ProductCategory.objects.update_or_create(
                subgroup_id=Category_id,
                menu=menu,
                defaults={
                    'subgroup_name': group['name'],
                    'order_index': group.get('order', 0),
                    'outer_data': group
                }
            )

        # 2. Link parents (только для созданных категорий)
        for group in groups:
            if group.get('isDeleted'):
                continue
            
            group_id = str(group['id'])
            # Пропускаем, если группа не была создана как категория
            if group_id not in used_group_ids:
                continue
            
            parent_id = group.get('parentGroup')
            if parent_id:
                try:
                    category = ProductCategory.objects.get(subgroup_id=group['id'], menu=menu)
                    parent = ProductCategory.objects.get(subgroup_id=parent_id, menu=menu)
                    # Проверяем, что родитель тоже является категорией (не группой модификаторов)
                    parent_id_str = str(parent_id)
                    if parent_id_str in used_group_ids:
                        category.parent = parent
                        category.save()
                except ProductCategory.DoesNotExist:
                    pass

    def _sync_products_and_modifiers(self, menu: Menu, organization: Organization, items: List[Dict], products_map: Dict[str, Dict] = None):
        if products_map is None:
             products_map = {p['id']: p for p in items}

        for item in items:
            if item.get('isDeleted'):
                continue
                
            item_type = item.get('type')
            
            # Treat 'Modifier' type items as potential independent products if needed, 
            # OR just ignore them here and process them only when embedded in Parent.
            # But sometimes modifiers are sold independently? 
            # For now, we process Dish/Good as Products.
            
            if item_type in ['Dish', 'Good']: 
                self._sync_product(menu, organization, item, products_map)
                
    def _sync_product(self, menu: Menu, organization: Organization, item: Dict, products_map: Dict[str, Dict]):
        import uuid
        product_id = item['id']
        category_id = item.get('groupId')
        parent_group_id = item.get('parentGroup')
        
        category = None
        if category_id:
            category = ProductCategory.objects.filter(subgroup_id=category_id, menu=menu).first()
        if not category and parent_group_id:
            category = ProductCategory.objects.filter(subgroup_id=parent_group_id, menu=menu).first()

        if not category:
            logger.warning(f"Category not found (groupId={category_id}, parentGroup={parent_group_id}) for product {item['name']}")

        price = 0
        size_prices = item.get('sizePrices', [])
        if size_prices:
            price_info = size_prices[0].get('price', {})
            price = price_info.get('currentPrice', 0)

        # Check modifiers availability
        group_modifiers = item.get('groupModifiers', [])
        simple_modifiers = item.get('modifiers', [])
        has_modifiers = bool(group_modifiers or simple_modifiers)

        # Поиск по (product_id, menu), чтобы продукты разных меню не перезаписывали друг друга
        product, created = Product.objects.update_or_create(
            product_id=product_id,
            menu=menu,
            defaults={
                'product_name': item['name'],
                'product_code': item.get('code'),
                'price': price,
                'description': item.get('description', ''),
                'measure_unit': item.get('measureUnit', 'порц'),
                'organization': organization,
                'category': category,
                'parent_group': category.subgroup_name if category else None,
                'order_index': item.get('order', 0),
                'image_url': item.get('imageLinks', [])[0] if item.get('imageLinks') else None,
                'type': item.get('type'),
                'outer_data': item,
                'has_modifiers': has_modifiers
            }
        )
        
        # Sync Modifiers if present
        if has_modifiers:
            self._sync_product_modifiers(product, group_modifiers, simple_modifiers, products_map)

    def _sync_product_modifiers(self, product, group_modifiers, simple_modifiers, products_map):
        import uuid
        # Clear existing modifiers to allow full resync
        Modifier.objects.filter(product=product).delete()
        
        # Helper to create modifier
        def create_modifier_entry(mod_data, group_info=None):
            # mod_data usually has 'id' (product id), 'minAmount', 'maxAmount', 'required'
            # OR it might include nested 'product' info.
            
            mod_product_id = mod_data.get('id') or mod_data.get('productId')
            if not mod_product_id:
                logger.warning(
                    f'Пропущен модификатор для продукта "{product.product_name}" (ID: {product.product_id}): '
                    f'отсутствует id или productId в данных: {mod_data}'
                )
                return

            # Lookup name/price from global map if missing
            name = mod_data.get('name') # unlikely in childModifiers
            price = mod_data.get('price') # unlikely?
            
            linked_product = products_map.get(mod_product_id)
            if linked_product:
                if not name: 
                    name = linked_product.get('name')
                # Price logic: usually modifier overrides price or adds to it?
                # If 'currentPrice' is in mod_data (sometimes), use it. Else use linked product price.
                # In iiko: childModifier might represent "Availability" of a product. Price might be 0 or override.
                if not price and 'price' in linked_product:
                    price = linked_product.get('price', 0)
            
            if not name:
                name = f"Modifier {mod_product_id}"

            # If create_modifier is just linking, we generate a new ID for the link
            # Конвертируем mod_product_id в строку для сохранения в modifier_code
            modifier_code_str = str(mod_product_id).strip() if mod_product_id else None
            
            if not modifier_code_str or modifier_code_str == 'None':
                logger.error(
                    f'Не удалось создать модификатор для продукта "{product.product_name}": '
                    f'modifier_code пустой или None после конвертации mod_product_id={mod_product_id}'
                )
                return
            
            Modifier.objects.create(
                modifier_id=uuid.uuid4(),
                modifier_name=name,
                product=product,
                modifier_code=modifier_code_str, # Keep iiko product ID here (as string)
                min_amount=int(mod_data.get('minAmount') or 0),
                max_amount=int(mod_data.get('maxAmount') or 1),
                is_required=bool(mod_data.get('required')) or bool(group_info and group_info.get('required')),
                price=float(price) if price is not None else 0.0
            )
            
            logger.debug(
                f'Создан модификатор для продукта "{product.product_name}": '
                f'name="{name}", modifier_code={modifier_code_str}'
            )

        # Process Group Modifiers
        for group in group_modifiers:
            child_mods = group.get('childModifiers', [])
            group_details = {
                'required': group.get('required', False),
                'minAmount': group.get('minAmount'),
                'maxAmount': group.get('maxAmount')
            }
            for child in child_mods:
                create_modifier_entry(child, group_details)

        # Process Simple Modifiers
        for mod in simple_modifiers:
            create_modifier_entry(mod)

    def _sync_modifier(self, item: Dict):
        # Placeholder for Modifier sync (if needed distinct from products)
        pass

    def sync_selected_roots(self, organization: Organization, menu_data: Dict[str, Any], root_ids: List[str]):
        """
        Syncs only selected Root Groups and their descendants.
        Each Root Group becomes a Menu.
        """
        if not menu_data:
            return

        all_groups = menu_data.get('groups', [])
        all_products = menu_data.get('products', [])
        
        # Build map for fast lookup
        groups_map = {g['id']: g for g in all_groups}
        
        # Helper to find all descendants
        def get_descendants(parent_id, accumulator):
            for g in all_groups:
                if g.get('parentGroup') == parent_id:
                    accumulator.add(g['id'])
                    get_descendants(g['id'], accumulator)

        with transaction.atomic():
            for root_id in root_ids:
                root_group = groups_map.get(root_id)
                if not root_group:
                    continue
                
                # Create Menu for this Root Group
                menu_name = root_group['name']
                menu, _ = Menu.objects.update_or_create(
                    organization=organization,
                    menu_name=menu_name,
                    defaults={}
                )
                
                # Identify all categories belonging to this tree
                # Start with empty set - we don't want root group to be a category
                relevant_category_ids = set()
                get_descendants(root_id, relevant_category_ids)
                
                # Filter groups to sync - EXCLUDE root group, only sync dependent groups as categories
                groups_to_sync = [g for g in all_groups if g['id'] in relevant_category_ids]
                
                # Sync these categories to THIS Menu (передаем products для фильтрации групп модификаторов)
                self._sync_categories(menu, groups_to_sync, all_products)
                
                # Sync Products: their 'groupId' (or parent) must be in relevant_category_ids OR root_id
                # Products in root group should still be synced, but without category assignment
                products_to_sync = [
                    p for p in all_products 
                    if p.get('groupId') in relevant_category_ids 
                    or (p.get('parentGroup') in relevant_category_ids)
                    or p.get('groupId') == root_id
                    or p.get('parentGroup') == root_id
                ]
                
                # Build map from ALL products for modifier lookup, not just synced ones
                if not 'products_map' in locals():
                    products_map = {p['id']: p for p in all_products}

                self._sync_products_and_modifiers(menu, organization, products_to_sync, products_map)

    def _price_for_category(
        self,
        item: Dict[str, Any],
        price_category_id: Optional[str],
        organization_id: Optional[str] = None,
    ) -> float:
        """Извлекает цену товара из ответа API v2. Универсально: если задана ценовая
        категория — сначала ищем по ней; если нет или не нашли — берём первую доступную
        цену (priceCategoryPrices, prices по organizationId/первая, price)."""
        def to_float(v):
            if v is None:
                return None
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        # 1) Предпочтительная ценовая категория (если задана)
        if price_category_id:
            price_cat_prices = item.get('priceCategoryPrices') or []
            for pcp in price_cat_prices:
                if str(pcp.get('priceCategoryId')) == str(price_category_id):
                    p = to_float(pcp.get('price'))
                    if p is not None:
                        return p
            for size in item.get('itemSizes') or []:
                for pcp in size.get('priceCategoryPrices') or []:
                    if str(pcp.get('priceCategoryId')) == str(price_category_id):
                        p = to_float(pcp.get('price'))
                        if p is not None:
                            return p

        # 2) Явная цена на уровне item
        p = to_float(item.get('price'))
        if p is not None:
            return p

        # 3) Первая доступная цена по ценовым категориям (если категория не подгрузилась)
        for pcp in item.get('priceCategoryPrices') or []:
            p = to_float(pcp.get('price'))
            if p is not None:
                return p
        for size in item.get('itemSizes') or []:
            for pcp in size.get('priceCategoryPrices') or []:
                p = to_float(pcp.get('price'))
                if p is not None:
                    return p
            # 4) prices: [{ organizationId, price }]
            size_prices = size.get('prices') or []
            if size_prices:
                for sp in size_prices:
                    if organization_id and str(sp.get('organizationId')) == str(organization_id):
                        p = to_float(sp.get('price'))
                        if p is not None:
                            return p
                p = to_float(size_prices[0].get('price'))
                if p is not None:
                    return p
            p = to_float(size.get('price'))
            if p is not None:
                return p
        return 0.0

    def sync_external_menu(
        self,
        organization: Organization,
        menu_data: Dict[str, Any],
        menu_name: str = None,
        price_category_id: Optional[str] = None,
        price_category_name: Optional[str] = None,
        external_menu_id: Optional[str] = None,
        set_active: bool = True,
    ):
        """
        Синхронизирует внешнее меню (ответ /api/2/menu/by_id) в БД.
        Запрос к iiko — только organizationIds и externalMenuId; из полученного
        меню выгружаем конкретную ценовую категорию: price_category_id задаёт,
        какую цену брать (priceCategoryPrices[].priceCategoryId или fallback на prices).
        """
        if not menu_data:
            logger.warning("No external menu data provided for sync")
            return

        item_categories = menu_data.get('itemCategories', [])

        with transaction.atomic():
            if not menu_name:
                menu_name = f"Внешнее меню {organization.org_name}"

            menu_metadata = {}
            if price_category_id:
                menu_metadata['price_category_id'] = str(price_category_id)
            if price_category_name:
                menu_metadata['price_category_name'] = price_category_name
            if external_menu_id:
                menu_metadata['external_menu_id'] = str(external_menu_id)

            menu, _ = Menu.objects.update_or_create(
                organization=organization,
                menu_name=menu_name,
                defaults={
                    'is_active': set_active,
                    'source_type': Menu.SOURCE_EXTERNAL,
                    'metadata': menu_metadata or None,
                }
            )
            if set_active:
                Menu.objects.filter(organization=organization).exclude(pk=menu.pk).update(is_active=False)

            for cat_data in item_categories:
                category_id = cat_data.get('id')
                category_name = cat_data.get('name')

                # Для каждого меню — свои категории (unique_together subgroup_id + menu)
                category, _ = ProductCategory.objects.update_or_create(
                    subgroup_id=category_id,
                    menu=menu,
                    defaults={
                        'subgroup_name': category_name,
                        'order_index': 0,
                        'outer_data': cat_data,
                    }
                )

                org_id = getattr(organization, 'iiko_organization_id', None)
                items = cat_data.get('items', [])
                for item in items:
                    product_id = item.get('id')
                    if not product_id and item.get('itemSizes'):
                        product_id = item['itemSizes'][0].get('itemId')
                    if not product_id:
                        continue
                    product_name = item.get('name', '')
                    price = self._price_for_category(item, price_category_id, organization_id=org_id)

                    item_sizes = item.get('itemSizes') or []
                    image_url = None
                    if item_sizes:
                        image_url = item_sizes[0].get('buttonImageUrl')

                    Product.objects.update_or_create(
                        product_id=product_id,
                        menu=menu,
                        defaults={
                            'product_name': product_name,
                            'product_code': item.get('sku'),
                            'price': price,
                            'description': item.get('description', ''),
                            'measure_unit': 'порц',
                            'organization': organization,
                            'category': category,
                            'parent_group': category_name,
                            'order_index': 0,
                            'image_url': image_url,
                            'type': 'Dish',
                            'outer_data': item,
                            'has_modifiers': bool(item.get('modifierSchemaId')),
                        }
                    )

    def sync_terminal_groups(self, terminal_groups_data: Dict[str, Any], organization: Organization = None):
        """
        Syncs terminal groups data from iiko to local database.
        """
        from apps.organizations.models import Terminal
        
        terminal_groups = terminal_groups_data.get('terminalGroups', [])
        synced_terminals = []

        with transaction.atomic():
            for org_data in terminal_groups:
                # org_data usually has 'organizationId' and 'items'
                items = org_data.get('items', [])
                for item in items:
                    terminal_id = item.get('id')
                    name = item.get('name')
                    
                    terminal, created = Terminal.objects.update_or_create(
                        terminal_id=terminal_id,
                        defaults={
                            'terminal_group_name': name,
                            'organization': organization,
                            'iiko_organization_id': organization.iiko_organization_id if organization else None,
                            'is_active': True
                        }
                    )
                    
                    synced_terminals.append(terminal)
        
        return synced_terminals

    def sync_payment_types(self, organization, payment_types_data: Dict[str, Any]):
        """
        Syncs payment types data from iiko to local database.
        """
        from apps.organizations.models import PaymentType
        
        payment_types = payment_types_data.get('paymentTypes', [])
        synced_types = []

        with transaction.atomic():
            for item in payment_types:
                if item.get('isDeleted'):
                    continue
                    
                payment_id = item.get('id')
                name = item.get('name')
                p_kind = item.get('paymentTypeKind', 'External')
                
                # Check if this payment_id already exists (since it's a PK)
                existing = PaymentType.objects.filter(payment_id=payment_id).first()
                if existing:
                    # If it exists, we just update it. 
                    # Note: this will reassign it to the current organization if it was linked elsewhere.
                    # This is a limitation of the current database schema where payment_id is PK.
                    existing.payment_name = name
                    existing.payment_type = p_kind
                    existing.organization = organization
                    existing.is_active = True
                    existing.save()
                    synced_types.append(existing)
                else:
                    payment_type_obj = PaymentType.objects.create(
                        payment_id=payment_id,
                        organization=organization,
                        payment_name=name,
                        payment_type=p_kind,
                        is_active=True
                    )
                    synced_types.append(payment_type_obj)
        
        return synced_types


def _extract_stop_list_items_for_terminal(
    api_response: Dict[str, Any], organization_id: str, terminal_id_str: str
) -> List[Dict]:
    """Из ответа get_stop_lists извлекает список items для одного терминала."""
    terminal_group_stop_lists = api_response.get('terminalGroupStopLists', [])
    for org_stop_list in terminal_group_stop_lists:
        if str(org_stop_list.get('organizationId')) != str(organization_id):
            continue
        for terminal_item in org_stop_list.get('items', []):
            tg_id = terminal_item.get('terminalGroupId')
            if tg_id and str(tg_id) == terminal_id_str:
                return terminal_item.get('items', [])
    return []


class StopListSyncService:
    """Сервис для синхронизации стоп-листа с iiko API"""
    
    def __init__(self, api_key: str):
        self.client = IikoClient(api_key)
    
    def apply_stop_list_response(self, terminal: Terminal, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Применяет уже полученный ответ get_stop_lists к одному терминалу (только БД).
        Используется для оптимизации: один запрос к API на организацию, затем обновление всех терминалов.
        """
        organization = terminal.organization
        if not organization:
            raise ValueError("Терминал должен быть привязан к организации")
        organization_id = organization.iiko_organization_id
        if not organization_id:
            raise ValueError("У организации должен быть настроен iiko_organization_id")
        terminal_id_str = str(terminal.terminal_id)
        items = _extract_stop_list_items_for_terminal(api_response, organization_id, terminal_id_str)
        return self._upsert_delete_stop_list_for_terminal(terminal, organization, items)

    def _upsert_delete_stop_list_for_terminal(
        self, terminal: Terminal, organization, items: List
    ) -> Dict[str, Any]:
        """UPSERT и DELETE записей стоп-листа для одного терминала в одной транзакции."""
        active_menu_product_pks = []  # Product.pk из активного меню (для корректного delete)
        created_count = 0
        updated_count = 0
        deleted_count = 0
        with transaction.atomic():
            for item in items:
                product_id_str = (
                    item.get('productId') or item.get('product_id') or item.get('id')
                )
                if not product_id_str:
                    continue
                try:
                    product_id = uuid.UUID(str(product_id_str))
                except (ValueError, TypeError):
                    continue
                product_name = (
                    item.get('productName') or item.get('product_name') or item.get('name') or ''
                )
                balance_value = (
                    item.get('balance') or item.get('quantity') or item.get('amount') or 0.0
                )
                try:
                    balance = float(balance_value)
                except (ValueError, TypeError):
                    balance = 0.0
                product = Product.objects.filter(
                    product_id=product_id,
                    organization=organization,
                    menu__is_active=True,
                ).first()
                if not product:
                    continue
                active_menu_product_pks.append(product.pk)
                stop_list_obj, created = StopList.objects.update_or_create(
                    product=product,
                    terminal=terminal,
                    defaults={
                        'product_name': product_name or product.product_name,
                        'balance': balance,
                        'organization': organization,
                        'is_auto_added': True,
                        'updated_at': timezone.now()
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            if active_menu_product_pks:
                deleted_queryset = StopList.objects.filter(terminal=terminal).exclude(
                    product_id__in=active_menu_product_pks
                )
                deleted_count = deleted_queryset.count()
                deleted_queryset.delete()
            else:
                deleted_queryset = StopList.objects.filter(terminal=terminal)
                deleted_count = deleted_queryset.count()
                deleted_queryset.delete()
        logger.info(
            f"Стоп-лист для терминала {terminal.terminal_id}: "
            f"создано {created_count}, обновлено {updated_count}, удалено {deleted_count}"
        )
        return {
            'terminal_id': str(terminal.terminal_id),
            'terminal_name': terminal.terminal_group_name,
            'created': created_count,
            'updated': updated_count,
            'deleted_count': deleted_count,
            'updated_count': len(active_menu_product_pks),
            'total_items': len(items)
        }

    def sync_stop_lists_for_terminals(self, terminals: List[Terminal]) -> List[Dict[str, Any]]:
        """
        Синхронизирует стоп-листы для списка терминалов одной организации.
        Делает один запрос к API на организацию вместо одного на каждый терминал.
        Обрабатываются только активные терминалы (is_active=True).
        """
        if not terminals:
            return []
        active_only = [t for t in terminals if t.is_active]
        if not active_only:
            return []
        organization = active_only[0].organization
        organization_id = organization.iiko_organization_id
        if not organization_id:
            raise ValueError("У организации должен быть настроен iiko_organization_id")
        api_response = self.client.get_stop_lists([organization_id])
        results = []
        for terminal in active_only:
            try:
                result = self.apply_stop_list_response(terminal, api_response)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Ошибка применения стоп-листа для терминала {terminal.terminal_id}: {e}",
                    exc_info=True
                )
        return results

    def sync_terminal_stop_list(self, terminal: Terminal) -> Dict[str, Any]:
        """
        Синхронизирует стоп-лист для конкретного терминала (только для активного).
        
        Логика:
        1. Запрос к API для получения актуального стоп-листа
        2. UPSERT для каждой позиции из ответа
        3. Smart DELETE для удаления записей, которых больше нет в API
        4. Все операции выполняются в одной транзакции
        5. Если API вернул ошибку, DELETE не выполняется
        """
        if not terminal.is_active:
            raise ValueError("Синхронизация стоп-листа доступна только для активных терминалов")
        if not terminal.organization:
            raise ValueError("Терминал должен быть привязан к организации")
        
        if not terminal.organization.api_key:
            raise ValueError("У организации должен быть настроен API ключ iiko")
        
        organization = terminal.organization
        organization_id = organization.iiko_organization_id
        
        if not organization_id:
            raise ValueError("У организации должен быть настроен iiko_organization_id")
        
        # Один запрос к API
        try:
            api_response = self.client.get_stop_lists([organization_id])
        except IikoAPIException as e:
            logger.error(f"Ошибка при запросе стоп-листа из iiko для терминала {terminal.terminal_id}: {e}")
            raise
        
        return self.apply_stop_list_response(terminal, api_response)

