# Migration: Organization — цвет оформления шапки TMA

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0015_terminal_instagram_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='primary_color',
            field=models.CharField(
                blank=True,
                default='#0284c7',
                max_length=7,
                null=True,
                verbose_name='Цвет оформления (шапка TMA)'
            ),
        ),
    ]
