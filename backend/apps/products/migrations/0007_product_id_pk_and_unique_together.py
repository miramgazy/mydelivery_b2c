# Migration: Product — new PK id, unique_together (product_id, menu)
# Порядок: добавить id -> снять FK на products -> обновить ссылки -> сменить PK -> вернуть FK.
# Если миграция падала раньше: откат — migrate products 0006; при необходимости
# ALTER TABLE products DROP COLUMN IF EXISTS id; затем снова migrate.

import uuid
from django.db import migrations, models


def fill_product_id(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for p in Product.objects.all():
        p.id = uuid.uuid4()
        p.save(update_fields=['id'])


def drop_fk_to_products(apps, schema_editor):
    """Снимаем все FK, ссылающиеся на products (имена генерирует Django)."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT conrelid::regclass::text AS tbl, conname
            FROM pg_constraint
            WHERE confrelid = 'products'::regclass AND contype = 'f'
        """)
        for row in cursor.fetchall():
            table, conname = row[0], row[1]
            # Идентификаторы в кавычках для PostgreSQL
            safe_table = table.split('.')[-1].strip('"').replace('"', '""')
            safe_conname = conname.replace('"', '""')
            cursor.execute(
                'ALTER TABLE "%s" DROP CONSTRAINT IF EXISTS "%s"' % (safe_table, safe_conname)
            )


def update_fks_to_new_pk(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    StopList = apps.get_model('products', 'StopList')
    Modifier = apps.get_model('products', 'Modifier')
    FastMenuItem = apps.get_model('products', 'FastMenuItem')
    OrderItem = apps.get_model('orders', 'OrderItem')
    id_by_old_pk = {str(p.product_id): str(p.id) for p in Product.objects.all()}
    for sl in StopList.objects.all():
        new_id = id_by_old_pk.get(str(sl.product_id))
        if new_id is not None:
            StopList.objects.filter(pk=sl.pk).update(product_id=new_id)
    for m in Modifier.objects.filter(product__isnull=False):
        new_id = id_by_old_pk.get(str(m.product_id))
        if new_id is not None:
            Modifier.objects.filter(pk=m.pk).update(product_id=new_id)
    for fi in FastMenuItem.objects.all():
        new_id = id_by_old_pk.get(str(fi.product_id))
        if new_id is not None:
            FastMenuItem.objects.filter(pk=fi.pk).update(product_id=new_id)
    for oi in OrderItem.objects.all():
        new_id = id_by_old_pk.get(str(oi.product_id))
        if new_id is not None:
            OrderItem.objects.filter(pk=oi.pk).update(product_id=new_id)


def noop_reverse(apps, schema_editor):
    pass


# После обновления ссылок: сменить PK и заново добавить FK (PostgreSQL).
# PROTECT в Django = RESTRICT в SQL (запрет удаления при наличии ссылок).
SWAP_PK_AND_ADD_FKS = """
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE products ADD CONSTRAINT products_pkey PRIMARY KEY (id);
ALTER TABLE stop_list ADD CONSTRAINT stop_list_product_id_fkey FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
ALTER TABLE modifiers ADD CONSTRAINT modifiers_product_id_fkey FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
ALTER TABLE fast_menu_items ADD CONSTRAINT fast_menu_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
ALTER TABLE order_items ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_menu_metadata'),
        ('orders', '0007_order_phone_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='id',
            field=models.UUIDField(null=True, default=uuid.uuid4, editable=False),
        ),
        migrations.RunPython(fill_product_id, noop_reverse),
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.UUIDField(null=False, default=uuid.uuid4, editable=False),
        ),
        migrations.RunPython(drop_fk_to_products, noop_reverse),
        migrations.RunPython(update_fks_to_new_pk, noop_reverse),
        migrations.RunSQL(
            SWAP_PK_AND_ADD_FKS,
            state_operations=[
                migrations.AlterField(
                    model_name='product',
                    name='product_id',
                    field=models.UUIDField(db_index=True, verbose_name='ID продукта (iiko)'),
                ),
                migrations.AlterField(
                    model_name='product',
                    name='id',
                    field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
                ),
            ],
            elidable=False,
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(
                fields=('product_id', 'menu'),
                name='products_product_id_menu_uniq',
            ),
        ),
    ]
