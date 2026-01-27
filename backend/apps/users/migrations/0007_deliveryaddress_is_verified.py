# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_billingphone"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliveryaddress",
            name="is_verified",
            field=models.BooleanField(
                default=False,
                help_text="Указывает, привязаны ли к адресу точные координаты latitude и longitude",
                verbose_name="Верифицирован",
            ),
        ),
    ]
