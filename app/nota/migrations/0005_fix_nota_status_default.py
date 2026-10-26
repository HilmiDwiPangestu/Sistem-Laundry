from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nota", "0004_alter_itempakaian_jenis_alter_nota_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nota",
            name="status",
            field=models.CharField(
                choices=[("Belum", "Belum selesai"), ("Sudah", "Selesai")],
                default="Belum",
                max_length=50,
            ),
        ),
    ]
