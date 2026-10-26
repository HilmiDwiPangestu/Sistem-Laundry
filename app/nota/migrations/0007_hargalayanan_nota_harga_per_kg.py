from django.db import migrations, models


def seed_harga_layanan(apps, schema_editor):
    HargaLayanan = apps.get_model("nota", "HargaLayanan")
    defaults = [
        ("express", "Express", 10000, 1),
        ("reguler_cuci_setrika", "Reguler - Cuci Setrika", 7000, 2),
        ("reguler_cuci_lipat", "Reguler - Cuci Lipat", 6000, 3),
        ("reguler_setrika", "Reguler - Setrika Saja", 5000, 4),
    ]
    for kode, nama, harga, urutan in defaults:
        HargaLayanan.objects.get_or_create(
            kode=kode,
            defaults={"nama": nama, "harga_per_kg": harga, "urutan": urutan},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("nota", "0006_alter_itempakaian_options_alter_nota_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="HargaLayanan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kode", models.CharField(max_length=40, unique=True)),
                ("nama", models.CharField(max_length=100)),
                ("harga_per_kg", models.PositiveIntegerField()),
                ("urutan", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Harga layanan",
                "verbose_name_plural": "Harga layanan",
                "ordering": ["urutan", "id"],
            },
        ),
        migrations.AddField(
            model_name="nota",
            name="harga_per_kg",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="nota",
            name="jenis",
            field=models.CharField(
                choices=[("cs", "Cuci Setrika"), ("c", "Cuci Lipat"), ("s", "Setrika Saja")],
                max_length=20,
            ),
        ),
        migrations.RunPython(seed_harga_layanan, migrations.RunPython.noop),
    ]
