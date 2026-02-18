# Generated migration for website_styles

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0018_add_discount_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteStyles',
            fields=[
                ('organization', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='website_styles',
                    serialize=False,
                    to='organizations.organization',
                    verbose_name='Организация'
                )),
                ('primary_color', models.CharField(
                    default='#FF5733',
                    max_length=7,
                    verbose_name='Основной цвет (кнопки, акценты)'
                )),
                ('secondary_color', models.CharField(
                    default='#333333',
                    max_length=7,
                    verbose_name='Второстепенный цвет (текст)'
                )),
                ('background_color', models.CharField(
                    default='#FFFFFF',
                    max_length=7,
                    verbose_name='Цвет фона'
                )),
                ('font_family', models.CharField(
                    default='Inter, sans-serif',
                    max_length=100,
                    verbose_name='Основной шрифт (Google Fonts)'
                )),
                ('border_radius', models.IntegerField(
                    default=12,
                    verbose_name='Скругление карточек и кнопок (px)'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Стили сайта',
                'verbose_name_plural': 'Стили сайтов',
                'db_table': 'website_styles',
            },
        ),
    ]
