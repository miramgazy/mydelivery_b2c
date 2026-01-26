# Исправление: Предотвращение создания категорий из групп модификаторов

## Проблема

При синхронизации меню из iiko API все группы из массива `groups` создавались как категории продуктов (`ProductCategory`), включая группы модификаторов. Это приводило к появлению лишних категорий в меню, которые не должны отображаться пользователям.

## Решение

Добавлена проверка в метод `_sync_categories`, которая определяет, используется ли группа продуктами:

1. **Создается множество `used_group_ids`** - ID всех групп, которые используются продуктами
2. **Группа считается используемой**, если у хотя бы одного продукта поле `groupId` или `parentGroup` равно ID этой группы
3. **Группы модификаторов пропускаются** - они не используются продуктами напрямую, а только через `groupModifiers` в структуре продукта

## Изменения в коде

### Метод `_sync_categories`

**До:**
```python
def _sync_categories(self, menu: Menu, groups: List[Dict]):
    for group in groups:
        if group.get('isDeleted'):
            continue
        # Создавалась категория для ВСЕХ групп
        ProductCategory.objects.update_or_create(...)
```

**После:**
```python
def _sync_categories(self, menu: Menu, groups: List[Dict], products: List[Dict] = None):
    # Определяем, какие группы используются продуктами
    used_group_ids = set()
    for product in products:
        group_id = product.get('groupId')
        parent_group_id = product.get('parentGroup')
        if group_id:
            used_group_ids.add(str(group_id))
        if parent_group_id:
            used_group_ids.add(str(parent_group_id))
    
    # Создаем категории только для используемых групп
    for group in groups:
        group_id = str(group['id'])
        if group_id not in used_group_ids:
            logger.debug(f"Skipping modifier group (no products): {group.get('name')}")
            continue
        # Создаем категорию только если группа используется
        ProductCategory.objects.update_or_create(...)
```

## Логика определения групп модификаторов

Группа модификаторов определяется как группа, которая:
- **НЕ используется** ни одним продуктом (нет продуктов с `groupId` или `parentGroup` равным ID группы)
- Используется только через `groupModifiers` в структуре продуктов

## Обновленные методы

1. **`sync_menu`** - передает `products` в `_sync_categories`
2. **`sync_selected_roots`** - передает `all_products` в `_sync_categories`
3. **`_sync_categories`** - теперь принимает `products` и фильтрует группы модификаторов

## Результат

- ✅ Группы модификаторов больше не создаются как категории
- ✅ В меню отображаются только реальные категории продуктов
- ✅ Модификаторы по-прежнему синхронизируются через `_sync_product_modifiers`
- ✅ Структура меню остается корректной

## Проверка

После синхронизации меню проверьте:
1. В админ-панели Django: `/admin/products/productcategory/`
2. Убедитесь, что нет категорий с названиями групп модификаторов
3. Проверьте, что модификаторы создаются только через `Modifier` модель, а не как категории

## Логирование

При пропуске группы модификаторов в логах будет сообщение:
```
Skipping modifier group (no products): <название группы> (ID: <uuid>)
```

Это нормальное поведение и не является ошибкой.
