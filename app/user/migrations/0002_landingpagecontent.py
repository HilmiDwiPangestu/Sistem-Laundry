from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LandingPageContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hero_badge", models.CharField(default="Laundry praktis untuk kebutuhan harian", max_length=80)),
                ("hero_title", models.CharField(default="Cucian bersih, rapi, dan siap menemani aktivitas Anda.", max_length=180)),
                ("hero_text", models.TextField(default="Sani Laundry membantu kebutuhan cuci harian dengan pilihan layanan yang sederhana, harga transparan, dan proses yang mudah dipahami.", max_length=420)),
                ("hero_primary_label", models.CharField(default="Lihat Layanan", max_length=50)),
                ("hero_secondary_label", models.CharField(default="Hubungi Kami", max_length=50)),
                ("about_kicker", models.CharField(default="Tentang Sani Laundry", max_length=60)),
                ("about_title", models.CharField(default="Layanan laundry yang dibuat sederhana dan dapat diandalkan.", max_length=160)),
                ("about_text", models.TextField(default="Kami melayani kebutuhan laundry reguler maupun express dengan alur yang jelas sejak cucian diterima hingga siap diambil.", max_length=700)),
                ("benefit_1_title", models.CharField(default="Harga jelas", max_length=80)),
                ("benefit_1_text", models.CharField(default="Tarif layanan dapat dilihat sebelum transaksi diproses.", max_length=220)),
                ("benefit_2_title", models.CharField(default="Pilihan layanan", max_length=80)),
                ("benefit_2_text", models.CharField(default="Tersedia reguler dan express sesuai kebutuhan pelanggan.", max_length=220)),
                ("benefit_3_title", models.CharField(default="Pencatatan rapi", max_length=80)),
                ("benefit_3_text", models.CharField(default="Setiap transaksi dicatat melalui nota agar lebih mudah dilacak.", max_length=220)),
                ("services_title", models.CharField(default="Pilih layanan yang paling sesuai.", max_length=140)),
                ("services_text", models.CharField(default="Harga layanan dikelola langsung dari sistem Sani Laundry dan dapat diperbarui kapan saja.", max_length=320)),
                ("service_express_text", models.CharField(default="Proses lebih cepat untuk kebutuhan mendesak.", max_length=180)),
                ("service_cuci_setrika_text", models.CharField(default="Cuci bersih dan rapi, siap digunakan.", max_length=180)),
                ("service_cuci_lipat_text", models.CharField(default="Pilihan praktis untuk cucian harian.", max_length=180)),
                ("service_setrika_text", models.CharField(default="Untuk pakaian bersih yang perlu dirapikan.", max_length=180)),
                ("process_title", models.CharField(default="Prosesnya singkat dan mudah", max_length=140)),
                ("process_text", models.CharField(default="Datang, pilih layanan, cucian kami proses, lalu ambil saat sudah selesai.", max_length=260)),
                ("process_step_1_title", models.CharField(default="Terima cucian", max_length=80)),
                ("process_step_1_text", models.CharField(default="Pilih layanan dan cucian dicatat dalam nota.", max_length=180)),
                ("process_step_2_title", models.CharField(default="Proses laundry", max_length=80)),
                ("process_step_2_text", models.CharField(default="Cucian diproses sesuai jenis layanan yang dipilih.", max_length=180)),
                ("process_step_3_title", models.CharField(default="Ambil cucian", max_length=80)),
                ("process_step_3_text", models.CharField(default="Simpan bukti transaksi untuk memudahkan pengambilan.", max_length=180)),
                ("cta_title", models.CharField(default="Butuh laundry hari ini?", max_length=150)),
                ("cta_text", models.CharField(default="Hubungi Sani Laundry untuk informasi layanan dan kebutuhan laundry Anda.", max_length=320)),
                ("footer_note", models.CharField(blank=True, default="Terima kasih telah mempercayakan kebutuhan laundry Anda kepada Sani Laundry.", max_length=180)),
                ("tampilkan_harga", models.BooleanField(default=True)),
                ("aktif", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Konten landing page",
                "verbose_name_plural": "Konten landing page",
            },
        ),
    ]
