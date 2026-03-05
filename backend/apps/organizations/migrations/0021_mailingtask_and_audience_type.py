from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0020_organization_yandex_maps_api_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailingTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название рассылки')),
                ('message_ru', models.TextField(blank=True, verbose_name='Текст сообщения (RU)')),
                ('message_kz', models.TextField(blank=True, verbose_name='Текст сообщения (KZ)')),
                (
                    'audience_type',
                    models.CharField(
                        choices=[
                            ('all', 'Всем'),
                            ('newbies', 'Новички (0 заказов)'),
                            ('sleepers_30', 'Спящие (30+ дней)'),
                            ('active_30', 'Активные (< 30 дней)'),
                        ],
                        default='all',
                        help_text='Тип аудитории для рассылки (всем, новички, спящие, активные)',
                        max_length=32,
                        verbose_name='Сегмент аудитории',
                    ),
                ),
                ('scheduled_at', models.DateTimeField(verbose_name='Время отправки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('draft', 'Черновик'),
                            ('scheduled', 'Запланирована'),
                            ('in_progress', 'В процессе'),
                            ('done', 'Завершена'),
                            ('error', 'Ошибка'),
                        ],
                        default='draft',
                        max_length=20,
                        verbose_name='Статус',
                    ),
                ),
                (
                    'total_recipients',
                    models.PositiveIntegerField(default=0, verbose_name='Всего получателей'),
                ),
                ('sent_ru', models.PositiveIntegerField(default=0, verbose_name='Успешно отправлено (RU)')),
                ('sent_kz', models.PositiveIntegerField(default=0, verbose_name='Успешно отправлено (KZ)')),
                ('failed_count', models.PositiveIntegerField(default=0, verbose_name='Технические ошибки')),
                (
                    'unsubscribed_count',
                    models.PositiveIntegerField(default=0, verbose_name='Отписались (403)'),
                ),
                (
                    'last_processed_user_id',
                    models.UUIDField(
                        blank=True,
                        help_text='UUID пользователя, на котором остановилась рассылка',
                        null=True,
                        verbose_name='Последний обработанный пользователь',
                    ),
                ),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='mailing_tasks',
                        to='organizations.organization',
                        verbose_name='Организация',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Рассылка',
                'verbose_name_plural': 'Рассылки',
                'db_table': 'mailing_tasks',
                'ordering': ['-created_at'],
            },
        ),
    ]

