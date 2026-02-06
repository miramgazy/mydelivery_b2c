# Migration: ProductCategory — new PK id, unique_together (subgroup_id, menu)
# Категории создаются заново для каждого меню при синхронизации.
# Перед сменой PK снимаем все FK, ссылающиеся на product_categories (products.category_id, product_categories.parent_id).

import uuid
from django.db import migrations, models


def backfill_category_id(apps, schema_editor):
    """Присвоить каждой категории уникальный id (БД могла заполнить default одним значением)."""
    ProductCategory = apps.get_model('products', 'ProductCategory')
    for cat in ProductCategory.objects.all():
        cat.id = uuid.uuid4()
        cat.save(update_fields=['id'])


def drop_fks_referencing_product_categories(apps, schema_editor):
    """Снять все FK, ссылающиеся на product_categories (имена генерирует Django)."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT conrelid::regclass::text AS tbl, conname
            FROM pg_constraint
            WHERE confrelid = 'product_categories'::regclass AND contype = 'f'
        """)
        for row in cursor.fetchall():
            table, conname = row[0], row[1]
            safe_table = table.split('.')[-1].strip('"').replace('"', '""')
            safe_conname = conname.replace('"', '""')
            cursor.execute(
                'ALTER TABLE "%s" DROP CONSTRAINT IF EXISTS "%s"' % (safe_table, safe_conname)
            )


def update_products_and_parent_fks_to_new_pk(apps, schema_editor):
    """Подставить в products.category_id и product_categories.parent_id новые id вместо subgroup_id."""
    ProductCategory = apps.get_model('products', 'ProductCategory')
    Product = apps.get_model('products', 'Product')
    subgroup_to_id = {str(c.subgroup_id): str(c.id) for c in ProductCategory.objects.all()}

    for p in Product.objects.exclude(category_id__isnull=True):
        old_pk = str(p.category_id)
        new_id = subgroup_to_id.get(old_pk)
        if new_id:
            Product.objects.filter(pk=p.pk).update(category_id=new_id)

    for cat in ProductCategory.objects.exclude(parent_id__isnull=True):
        old_parent_pk = str(cat.parent_id)
        new_parent_id = subgroup_to_id.get(old_parent_pk)
        if new_parent_id:
            ProductCategory.objects.filter(pk=cat.pk).update(parent_id=new_parent_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_product_id_pk_and_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(backfill_category_id, noop_reverse),
        migrations.RunPython(drop_fks_referencing_product_categories, noop_reverse),
        migrations.RunPython(update_products_and_parent_fks_to_new_pk, noop_reverse),
        migrations.RunSQL(
            [
                "ALTER TABLE product_categories ALTER COLUMN id SET NOT NULL;",
                "ALTER TABLE product_categories DROP CONSTRAINT IF EXISTS product_categories_pkey;",
                "ALTER TABLE product_categories ADD PRIMARY KEY (id);",
                "CREATE UNIQUE INDEX IF NOT EXISTS product_categories_subgroup_menu_uniq ON product_categories (subgroup_id, menu_id);",
                "ALTER TABLE products ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE SET NULL;",
                "ALTER TABLE product_categories ADD CONSTRAINT product_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE SET NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE product_categories DROP CONSTRAINT IF EXISTS product_categories_parent_id_fkey;",
                "ALTER TABLE products DROP CONSTRAINT IF EXISTS products_category_id_fkey;",
                "DROP INDEX IF EXISTS product_categories_subgroup_menu_uniq;",
                "ALTER TABLE product_categories DROP CONSTRAINT IF EXISTS product_categories_pkey;",
                "ALTER TABLE product_categories ADD PRIMARY KEY (subgroup_id);",
                "ALTER TABLE product_categories ALTER COLUMN id DROP NOT NULL;",
                "ALTER TABLE products ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES product_categories(subgroup_id) ON DELETE SET NULL;",
                "ALTER TABLE product_categories ADD CONSTRAINT product_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES product_categories(subgroup_id) ON DELETE SET NULL;",
            ],
        ),
        # Только состояние: RunSQL уже изменил БД (PK и индекс), не выполнять SQL снова
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='productcategory',
                    name='id',
                    field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name='productcategory',
                    name='subgroup_id',
                    field=models.UUIDField(db_index=True, verbose_name='ID подгруппы (iiko)'),
                ),
                migrations.AlterField(
                    model_name='productcategory',
                    name='menu',
                    field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='categories', to='products.menu', verbose_name='Меню'),
                ),
                migrations.AddConstraint(
                    model_name='productcategory',
                    constraint=models.UniqueConstraint(fields=('subgroup_id', 'menu'), name='product_categories_subgroup_menu_uniq'),
                ),
            ],
            database_operations=[],
        ),
    ]
