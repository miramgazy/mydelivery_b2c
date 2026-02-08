# Migration: FastMenuGroup — add image field for tile picture

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_productcategory_id_pk_and_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='fastmenugroup',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='fast_menu/', verbose_name='Изображение'),
        ),
    ]
