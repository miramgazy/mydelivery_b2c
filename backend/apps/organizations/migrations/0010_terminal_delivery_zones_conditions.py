# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0009_terminal_stop_list_interval_min"),
    ]

    operations = [
        migrations.AddField(
            model_name="terminal",
            name="delivery_zones_conditions",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Массив объектов зон доставки с координатами, названием, приоритетом, цветом и типом доставки",
                null=True,
                verbose_name="Условия зон доставки",
            ),
        ),
    ]
