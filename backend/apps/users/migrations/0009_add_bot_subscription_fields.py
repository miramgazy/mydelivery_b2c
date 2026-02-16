# Generated manually for bot subscription consent flow

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_add_user_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_bot_subscribed',
            field=models.BooleanField(
                default=None,
                help_text='True — подписан, False — отказался, None — не выбирал',
                null=True,
                verbose_name='Подписан на уведомления бота'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='chat_id',
            field=models.BigIntegerField(
                blank=True,
                help_text='Telegram chat_id для отправки уведомлений',
                null=True,
                verbose_name='ID чата с ботом'
            ),
        ),
        migrations.CreateModel(
            name='BotSyncToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bot_sync_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID для Deep Link')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_sync_tokens', to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Токен синхронизации бота',
                'verbose_name_plural': 'Токены синхронизации бота',
                'db_table': 'bot_sync_tokens',
            },
        ),
    ]
