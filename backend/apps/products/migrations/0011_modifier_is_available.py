# Generated manually for modifier soft-deactivation (sync with iiko)

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0010_fix_unreflected_model_changes"),
    ]

    operations = [
        migrations.AddField(
            model_name="modifier",
            name="is_available",
            field=models.BooleanField(
                default=True,
                verbose_name="Доступен (есть в текущей выгрузке iiko)",
            ),
        ),
        migrations.AddIndex(
            model_name="modifier",
            index=models.Index(fields=["is_available"], name="modifiers_is_avail_idx"),
        ),
    ]
