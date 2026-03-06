# Migration: retry_count и статус SentToBackupWebhook для умного повтора

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_iikorequestlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='retry_count',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Количество повторов в iiko'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Ожидает'),
                    ('confirmed', 'Подтвержден'),
                    ('preparing', 'Готовится'),
                    ('delivering', 'Доставляется'),
                    ('completed', 'Завершен'),
                    ('cancelled', 'Отменен'),
                    ('error', 'Ошибка'),
                    ('InProgress', 'В процессе iiko'),
                    ('Success', 'Успешно создан в iiko'),
                    ('SentToBackupWebhook', 'Отправлен на резервный вебхук'),
                ],
                default='pending',
                max_length=50,
                verbose_name='Статус',
            ),
        ),
    ]
