# Migration: IikoRequestLog — таблица логов итоговых JSON запросов к iikoCloud

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_phone_blank'),
    ]

    operations = [
        migrations.CreateModel(
            name='IikoRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payload', models.JSONField(help_text='Склеенный JSON перед отправкой', verbose_name='Итоговый JSON запроса')),
                ('success', models.BooleanField(default=False, verbose_name='Успешно отправлен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('order', models.ForeignKey(db_column='order_id', on_delete=models.deletion.CASCADE, related_name='iiko_request_logs', to='orders.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Лог запроса iiko',
                'verbose_name_plural': 'Логи запросов iiko',
                'db_table': 'iiko_request_logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
