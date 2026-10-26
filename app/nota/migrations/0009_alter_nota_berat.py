from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nota", "0008_pengaturanlaundry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nota",
            name="berat",
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
    ]
