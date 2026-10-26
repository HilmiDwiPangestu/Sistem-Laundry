from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nota", "0007_hargalayanan_nota_harga_per_kg"),
    ]

    operations = [
        migrations.CreateModel(
            name="PengaturanLaundry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nama_usaha", models.CharField(default="Sani Laundry", max_length=100)),
                ("slogan", models.CharField(blank=True, default="Bersih • Wangi • Rapi", max_length=120)),
                ("alamat", models.CharField(blank=True, default="", max_length=220)),
                ("telepon", models.CharField(blank=True, default="", max_length=40)),
                ("lebar_kertas", models.PositiveSmallIntegerField(choices=[(58, "58 mm"), (80, "80 mm")], default=58)),
                ("tampilkan_logo", models.BooleanField(default=True)),
                ("tampilkan_item", models.BooleanField(default=True)),
                ("footer_struk", models.CharField(blank=True, default="Terima kasih telah mempercayakan laundry Anda kepada Sani Laundry.", max_length=220)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Pengaturan laundry",
                "verbose_name_plural": "Pengaturan laundry",
            },
        ),
    ]
