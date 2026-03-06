# Migration: webhook_link для резервной отправки заказов

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0021_mailingtask_and_audience_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='webhook_link',
            field=models.URLField(
                blank=True,
                help_text='URL для отправки заказа при сбое доставки в iiko (умный повтор)',
                max_length=500,
                null=True,
                verbose_name='Ссылка для резервной отправки заказов'
            ),
        ),
    ]
