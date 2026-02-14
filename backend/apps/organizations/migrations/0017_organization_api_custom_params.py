# Migration: Organization — кастомные параметры iiko API

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0016_organization_primary_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='api_custom_params',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'JSON-объект для наложения на запрос к iikoCloud API. '
                    'Параметры в "order" добавляются в блок заказа, на верхнем уровне — в корень. '
                    'Пример: {"order": {"comment": "Доставить быстро"}, "createOrderSettings": {"servicePrint": true}}'
                ),
                null=True,
                verbose_name='Кастомные параметры iiko API'
            ),
        ),
    ]
