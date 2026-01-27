# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0011_city_city_id_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="terminal",
            name="working_hours",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Рабочее время терминала в формате {'start': 'HH:mm', 'end': 'HH:mm'}",
                null=True,
                verbose_name="Рабочее время",
            ),
        ),
    ]
