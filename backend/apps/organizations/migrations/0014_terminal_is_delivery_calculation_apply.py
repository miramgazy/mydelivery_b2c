# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0013_paymenttype_system_type_alter_paymenttype_payment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="terminal",
            name="is_delivery_calculation_apply",
            field=models.BooleanField(
                default=False,
                help_text="Если включено, для этого терминала будет применяться расчет стоимости доставки на основе зон",
                verbose_name="Применять расчет стоимости доставки",
            ),
        ),
    ]
