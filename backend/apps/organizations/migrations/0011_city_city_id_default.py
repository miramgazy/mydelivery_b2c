# Generated manually

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organizations", "0010_terminal_delivery_zones_conditions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="city",
            name="city_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
