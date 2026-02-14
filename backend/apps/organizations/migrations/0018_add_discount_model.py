# Migration: Discount model for iikoCloud API sync

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0017_organization_api_custom_params'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.UUIDField(db_index=True, unique=True, verbose_name='ID в iiko')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('percent', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Процент')),
                ('mode', models.CharField(default='Percent', max_length=50, verbose_name='Режим')),
                ('is_manual', models.BooleanField(default=False, verbose_name='Ручная')),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='True, если скидка пришла в последнем ответе API',
                    verbose_name='Активна'
                )),
                ('is_deleted_in_iiko', models.BooleanField(
                    default=False,
                    help_text='Значение поля isDeleted из API',
                    verbose_name='Удалена в iiko'
                )),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='discounts',
                    to='organizations.organization',
                    verbose_name='Организация'
                )),
            ],
            options={
                'verbose_name': 'Скидка',
                'verbose_name_plural': 'Скидки',
                'db_table': 'discounts',
                'ordering': ['-is_active', 'name'],
            },
        ),
    ]
