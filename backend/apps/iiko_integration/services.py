import logging
from typing import Dict, Any, List
from django.db import transaction
from apps.products.models import Menu, ProductCategory, Product, Modifier
from apps.organizations.models import Organization

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

            # 2. Process Groups (Categories)
            groups = menu_data.get('groups', [])
            self._sync_categories(menu, groups)

            # 3. Process Products & Modifiers
            products = menu_data.get('products', [])
            # Map for quick lookup of modifier names
            products_map = {p['id']: p for p in products}
            
            self._sync_products_and_modifiers(menu, organization, products, products_map)

    def _sync_categories(self, menu: Menu, groups: List[Dict]):
        # 1. Create/Update all (preserving structure logic from before)
        for group in groups:
            if group.get('isDeleted'):
                continue

            Category_id = group['id']
            ProductCategory.objects.update_or_create(
                subgroup_id=Category_id,
                defaults={
                    'subgroup_name': group['name'],
                    'menu': menu,
                    'order_index': group.get('order', 0),
                    'outer_data': group
                }
            )

        # 2. Link parents
        for group in groups:
            if group.get('isDeleted'):
                continue
            
            parent_id = group.get('parentGroup')
            if parent_id:
                try:
                    category = ProductCategory.objects.get(subgroup_id=group['id'])
                    parent = ProductCategory.objects.get(subgroup_id=parent_id)
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
        # Try finding category by groupId first, then by parentGroup
        if category_id:
            category = ProductCategory.objects.filter(subgroup_id=category_id).first()
        
        if not category and parent_group_id:
            category = ProductCategory.objects.filter(subgroup_id=parent_group_id).first()

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

        product, created = Product.objects.update_or_create(
            product_id=product_id,
            defaults={
                'product_name': item['name'],
                'product_code': item.get('code'),
                'price': price,
                'description': item.get('description', ''),
                'measure_unit': item.get('measureUnit', 'порц'),
                'organization': organization,
                'menu': menu,
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
                return

            # Lookup name/price from global map if missing
            name = mod_data.get('name') # unlikely in childModifiers
            price = mod_data.get('price') # unlikely?
            
            linked_product = products_map.get(mod_product_id)
            if linked_product:
                if not name: name = linked_product.get('name')
                # Price logic: usually modifier overrides price or adds to it?
                # If 'currentPrice' is in mod_data (sometimes), use it. Else use linked product price.
                # In iiko: childModifier might represent "Availability" of a product. Price might be 0 or override.
                pass
            
            if not name:
                name = f"Modifier {mod_product_id}"

            # If create_modifier is just linking, we generate a new ID for the link
            Modifier.objects.create(
                modifier_id=uuid.uuid4(),
                modifier_name=name,
                product=product,
                modifier_code=mod_product_id, # Keep iiko product ID here
                min_amount=int(mod_data.get('minAmount') or 0),
                max_amount=int(mod_data.get('maxAmount') or 1),
                is_required=bool(mod_data.get('required')) or bool(group_info and group_info.get('required')),
                price=0 # simplified for now, as price logic is complex in iiko
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
                relevant_category_ids = {root_id}
                get_descendants(root_id, relevant_category_ids)
                
                # Filter groups to sync
                # Note: Root group itself is the Menu, so we might NOT want to make it a Category?
                # User said: "Root group is the menu name". 
                # If we create a Category for it too, it will be a "root category" in that Menu.
                # Let's filter groups list to include only those in relevant_category_ids
                # BUT EXCLUDING the root itself if we treat it purely as Menu container?
                # Usually better to have strictly hierarchical categories inside.
                # Let's include all relevant IDs as categories for now, attached to this Menu.
                
                groups_to_sync = [g for g in all_groups if g['id'] in relevant_category_ids]
                
                # Sync these categories to THIS Menu
                self._sync_categories(menu, groups_to_sync)
                
                # Sync Products: their 'groupId' (or parent) must be in relevant_category_ids
                products_to_sync = [
                    p for p in all_products 
                    if p.get('groupId') in relevant_category_ids 
                    or (p.get('parentGroup') in relevant_category_ids)
                ]
                
                # Build map from ALL products for modifier lookup, not just synced ones
                if not 'products_map' in locals():
                    products_map = {p['id']: p for p in all_products}

                self._sync_products_and_modifiers(menu, organization, products_to_sync, products_map)

    def sync_external_menu(self, organization: Organization, menu_data: Dict[str, Any], menu_name: str = None):
        """
        Syncs external menu data (from /api/2/menu/by_id) to local database.
        """
        if not menu_data:
            logger.warning("No external menu data provided for sync")
            return

        item_categories = menu_data.get('itemCategories', [])
        
        with transaction.atomic():
            # 1. Ensure Menu exists
            if not menu_name:
                 menu_name = f"Внешнее меню {organization.org_name}"
            
            menu, _ = Menu.objects.update_or_create(
                organization=organization,
                menu_name=menu_name,
                defaults={'is_active': True}
            )

            for cat_data in item_categories:
                category_id = cat_data.get('id')
                category_name = cat_data.get('name')
                
                # Sync Category
                category, _ = ProductCategory.objects.update_or_create(
                    subgroup_id=category_id,
                    defaults={
                        'subgroup_name': category_name,
                        'menu': menu,
                        'order_index': 0, # v2 doesn't always have order here
                        'outer_data': cat_data
                    }
                )

                # Sync Products in this category
                items = cat_data.get('items', [])
                for item in items:
                    product_id = item.get('id')
                    product_name = item.get('name')
                    
                    price = item.get('price', 0)
                    # If there are sizes, we might want to pick the first one's price
                    item_sizes = item.get('itemSizes', [])
                    if item_sizes and not price:
                        price = item_sizes[0].get('price', 0)

                    # v2 sometimes has image in itemSizes or buttonImageUrl
                    image_url = None
                    if item_sizes:
                        image_url = item_sizes[0].get('buttonImageUrl')

                    Product.objects.update_or_create(
                        product_id=product_id,
                        defaults={
                            'product_name': product_name,
                            'product_code': item.get('sku'),
                            'price': price,
                            'description': item.get('description', ''),
                            'measure_unit': 'порц', # simplified
                            'organization': organization,
                            'menu': menu,
                            'category': category,
                            'parent_group': category_name,
                            'order_index': 0,
                            'image_url': image_url,
                            'type': 'Dish', # Assume Dish for external menu
                            'outer_data': item,
                            'has_modifiers': bool(item.get('modifierSchemaId'))
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
