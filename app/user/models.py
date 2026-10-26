from django.db import models


class ItemLaundry(models.Model):
    """Model lama dipertahankan agar migrasi dan data lama tetap kompatibel."""

    PILIHAN_PAKAIAN = [
        ("kaos_pendek", "Kaos Lengan Pendek"),
        ("kaos_panjang", "Kaos Lengan Panjang"),
        ("kemeja_pendek", "Kemeja Lengan Pendek"),
        ("kemeja_panjang", "Kemeja Lengan Panjang"),
        ("celana_pendek", "Celana Pendek"),
        ("celana_panjang", "Celana Panjang"),
        ("jaket", "Jaket"),
        ("sweater", "Sweater"),
        ("hoodie", "Hoodie"),
        ("lainnya", "Lainnya"),
    ]

    jenis_pakaian = models.CharField(max_length=50, choices=PILIHAN_PAKAIAN)
    jumlah = models.IntegerField(default=1)
    keterangan = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_jenis_pakaian_display()} - {self.jumlah}"


class LandingPageContent(models.Model):
    """Konten landing page yang dapat dikelola admin tanpa mengubah source code.

    Aplikasi hanya memakai satu baris (singleton, pk=1). Pemisahan model ini membuat
    bagian publik tidak tercampur dengan transaksi karyawan, tetapi tetap mudah
    dikelola dari Admin Center.
    """

    hero_badge = models.CharField(
        max_length=80,
        default="Laundry praktis untuk kebutuhan harian",
    )
    hero_title = models.CharField(
        max_length=180,
        default="Cucian bersih, rapi, dan siap menemani aktivitas Anda.",
    )
    hero_text = models.TextField(
        max_length=420,
        default=(
            "Sani Laundry membantu kebutuhan cuci harian dengan pilihan layanan yang "
            "sederhana, harga transparan, dan proses yang mudah dipahami."
        ),
    )
    hero_primary_label = models.CharField(max_length=50, default="Lihat Layanan")
    hero_secondary_label = models.CharField(max_length=50, default="Hubungi Kami")

    about_kicker = models.CharField(max_length=60, default="Tentang Sani Laundry")
    about_title = models.CharField(
        max_length=160,
        default="Layanan laundry yang dibuat sederhana dan dapat diandalkan.",
    )
    about_text = models.TextField(
        max_length=700,
        default=(
            "Kami melayani kebutuhan laundry reguler maupun express dengan alur yang "
            "jelas sejak cucian diterima hingga siap diambil."
        ),
    )

    benefit_1_title = models.CharField(max_length=80, default="Harga jelas")
    benefit_1_text = models.CharField(
        max_length=220,
        default="Tarif layanan dapat dilihat sebelum transaksi diproses.",
    )
    benefit_2_title = models.CharField(max_length=80, default="Pilihan layanan")
    benefit_2_text = models.CharField(
        max_length=220,
        default="Tersedia reguler dan express sesuai kebutuhan pelanggan.",
    )
    benefit_3_title = models.CharField(max_length=80, default="Pencatatan rapi")
    benefit_3_text = models.CharField(
        max_length=220,
        default="Setiap transaksi dicatat melalui nota agar lebih mudah dilacak.",
    )

    services_title = models.CharField(max_length=140, default="Pilih layanan yang paling sesuai.")
    services_text = models.CharField(
        max_length=320,
        default="Harga layanan dikelola langsung dari sistem Sani Laundry dan dapat diperbarui kapan saja.",
    )
    service_express_text = models.CharField(max_length=180, default="Proses lebih cepat untuk kebutuhan mendesak.")
    service_cuci_setrika_text = models.CharField(max_length=180, default="Cuci bersih dan rapi, siap digunakan.")
    service_cuci_lipat_text = models.CharField(max_length=180, default="Pilihan praktis untuk cucian harian.")
    service_setrika_text = models.CharField(max_length=180, default="Untuk pakaian bersih yang perlu dirapikan.")

    process_title = models.CharField(max_length=140, default="Prosesnya singkat dan mudah")
    process_text = models.CharField(
        max_length=260,
        default="Datang, pilih layanan, cucian kami proses, lalu ambil saat sudah selesai.",
    )
    process_step_1_title = models.CharField(max_length=80, default="Terima cucian")
    process_step_1_text = models.CharField(max_length=180, default="Pilih layanan dan cucian dicatat dalam nota.")
    process_step_2_title = models.CharField(max_length=80, default="Proses laundry")
    process_step_2_text = models.CharField(max_length=180, default="Cucian diproses sesuai jenis layanan yang dipilih.")
    process_step_3_title = models.CharField(max_length=80, default="Ambil cucian")
    process_step_3_text = models.CharField(max_length=180, default="Simpan bukti transaksi untuk memudahkan pengambilan.")

    cta_title = models.CharField(
        max_length=150,
        default="Butuh laundry hari ini?",
    )
    cta_text = models.CharField(
        max_length=320,
        default="Hubungi Sani Laundry untuk informasi layanan dan kebutuhan laundry Anda.",
    )
    footer_note = models.CharField(
        max_length=180,
        blank=True,
        default="Terima kasih telah mempercayakan kebutuhan laundry Anda kepada Sani Laundry.",
    )
    tampilkan_harga = models.BooleanField(default=True)
    aktif = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten landing page"
        verbose_name_plural = "Konten landing page"

    def __str__(self):
        return "Konten Landing Page Sani Laundry"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
