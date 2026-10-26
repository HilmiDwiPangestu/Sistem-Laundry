from decimal import Decimal

from django.db import models


DEFAULT_HARGA_LAYANAN = {
    "express": {
        "nama": "Express",
        "harga_per_kg": 10000,
        "urutan": 1,
    },
    "reguler_cuci_setrika": {
        "nama": "Reguler - Cuci Setrika",
        "harga_per_kg": 7000,
        "urutan": 2,
    },
    "reguler_cuci_lipat": {
        "nama": "Reguler - Cuci Lipat",
        "harga_per_kg": 6000,
        "urutan": 3,
    },
    "reguler_setrika": {
        "nama": "Reguler - Setrika Saja",
        "harga_per_kg": 5000,
        "urutan": 4,
    },
}


class Pelanggan(models.Model):
    JNS_PLGGN = (
        ("umum", "Umum"),
        ("lpk", "LPK"),
        ("sekolah", "Sekolah"),
    )

    nama = models.CharField(max_length=100)
    alamat = models.CharField(max_length=200, blank=True, null=True)
    jenis_plggn = models.CharField(max_length=20, choices=JNS_PLGGN, default="umum")

    class Meta:
        ordering = ["nama"]

    def __str__(self):
        return self.nama


class HargaLayanan(models.Model):
    """Master harga per kilogram yang dapat diubah dari panel pegawai."""

    kode = models.CharField(max_length=40, unique=True)
    nama = models.CharField(max_length=100)
    harga_per_kg = models.PositiveIntegerField()
    urutan = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["urutan", "id"]
        verbose_name = "Harga layanan"
        verbose_name_plural = "Harga layanan"

    def __str__(self):
        return f"{self.nama} - Rp{self.harga_per_kg:,}/kg"

    @classmethod
    def kode_dari_nota(cls, layanan, jenis):
        if layanan == "express":
            return "express"
        mapping = {
            "cs": "reguler_cuci_setrika",
            "c": "reguler_cuci_lipat",
            "s": "reguler_setrika",
        }
        return mapping.get(jenis, "reguler_cuci_setrika")


def get_harga_layanan_map():
    """Mengambil master harga dan memakai default bila suatu baris belum tersedia."""
    hasil = {
        kode: data["harga_per_kg"]
        for kode, data in DEFAULT_HARGA_LAYANAN.items()
    }
    for row in HargaLayanan.objects.filter(kode__in=hasil.keys()).only("kode", "harga_per_kg"):
        hasil[row.kode] = row.harga_per_kg
    return hasil


def get_harga_per_kg(layanan, jenis):
    kode = HargaLayanan.kode_dari_nota(layanan, jenis)
    return get_harga_layanan_map()[kode]


def bulatkan_ribuan(nilai):
    """
    Pembulatan sesuai aturan operasional Sani Laundry:
    sisa sampai Rp500 dibulatkan turun, sisa di atas Rp500 dibulatkan naik.

    Contoh:
    12.300 -> 12.000
    12.500 -> 12.000
    12.600 -> 13.000
    """
    nilai = Decimal(str(nilai))
    dasar = (nilai // Decimal("1000")) * Decimal("1000")
    sisa = nilai - dasar
    if sisa > Decimal("500"):
        dasar += Decimal("1000")
    return int(dasar)


def hitung_total_harga(berat, harga_per_kg):
    return bulatkan_ribuan(Decimal(str(berat)) * Decimal(str(harga_per_kg)))


class PengaturanLaundry(models.Model):
    """Pengaturan ringan untuk identitas usaha dan struk thermal.

    Hanya satu baris dipakai (singleton) agar pegawai tidak perlu mengelola
    banyak konfigurasi. Nilai dapat diubah dari Control Center.
    """

    PAPER_WIDTH = ((58, "58 mm"), (80, "80 mm"))

    nama_usaha = models.CharField(max_length=100, default="Sani Laundry")
    slogan = models.CharField(max_length=120, blank=True, default="Bersih • Wangi • Rapi")
    alamat = models.CharField(max_length=220, blank=True, default="")
    telepon = models.CharField(max_length=40, blank=True, default="")
    lebar_kertas = models.PositiveSmallIntegerField(choices=PAPER_WIDTH, default=58)
    tampilkan_logo = models.BooleanField(default=True)
    tampilkan_item = models.BooleanField(default=True)
    footer_struk = models.CharField(
        max_length=220,
        blank=True,
        default="Terima kasih telah mempercayakan laundry Anda kepada Sani Laundry.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pengaturan laundry"
        verbose_name_plural = "Pengaturan laundry"

    def __str__(self):
        return "Pengaturan Sani Laundry"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Nota(models.Model):
    JENIS = (
        ("cs", "Cuci Setrika"),
        ("c", "Cuci Lipat"),
        ("s", "Setrika Saja"),
    )

    LAYANAN = (
        ("reguler", "Reguler"),
        ("express", "Express"),
    )

    # Nilai database lama tetap dipertahankan agar data lama aman.
    STATUS = (
        ("Belum", "Belum selesai"),
        ("Sudah", "Selesai"),
    )

    pelanggan = models.ForeignKey(
        Pelanggan,
        on_delete=models.CASCADE,
        related_name="notas",
    )
    # Decimal dipakai agar berat seperti 3,81 atau 3,815 kg tersimpan presisi.
    berat = models.DecimalField(max_digits=8, decimal_places=3)
    jenis = models.CharField(max_length=20, choices=JENIS)
    layanan = models.CharField(max_length=20, choices=LAYANAN)
    status = models.CharField(max_length=50, choices=STATUS, default="Belum")
    harga_per_kg = models.PositiveIntegerField(blank=True, null=True)
    harga = models.IntegerField()
    tgl = models.DateField()

    class Meta:
        ordering = ["-tgl", "-id"]

    def __str__(self):
        return f"#{self.id} - {self.pelanggan.nama}"

    @property
    def nomor_struk(self):
        if not self.id or not self.tgl:
            return "SL-BARU"
        return f"SL-{self.tgl:%y%m%d}-{self.id:04d}"

    @property
    def total_item(self):
        return sum(item.jumlah for item in self.items.all())

    @property
    def harga_sebelum_pembulatan(self):
        if not self.harga_per_kg:
            return None
        return int(Decimal(str(self.berat)) * Decimal(str(self.harga_per_kg)))

    def terapkan_harga_otomatis(self):
        self.harga_per_kg = get_harga_per_kg(self.layanan, self.jenis)
        self.harga = hitung_total_harga(self.berat, self.harga_per_kg)
        return self.harga


class ItemPakaian(models.Model):
    JENIS_PAKAIAN = [
        ("Kaos L. Pendek", "Kaos Lengan Pendek"),
        ("Kaos L. Panjang", "Kaos Lengan Panjang"),
        ("Kemeja L. Pendek", "Kemeja Lengan Pendek"),
        ("Kemeja L. Panjang", "Kemeja Lengan Panjang"),
        ("Celana Panjang", "Celana Panjang"),
        ("Celana Pendek", "Celana Pendek"),
        ("Celana Dalam", "Celana Dalam"),
        ("Kerudung", "Kerudung"),
        ("Jaket", "Jaket"),
        ("Sprei", "Sprei"),
        ("Selimut", "Selimut"),
        ("Sarung Bantal", "Sarung Bantal"),
        ("Daster", "Daster"),
        ("Sarung", "Sarung"),
        ("Polo Osin", "Polo Osin"),
        ("Kemeja Osin", "Kemeja Osin"),
        ("Sajadah", "Sajadah"),
        ("Training Osin", "Training Osin"),
        ("Batik Osin", "Batik Osin"),
        ("Koko Osin", "Koko Osin"),
        ("Kupluk", "Kupluk"),
        ("Dasi", "Dasi"),
        ("Jas", "Jas"),
        ("Kaos Osin", "Kaos Osin"),
        ("Baju Koko", "Baju Koko"),
        ("Gamis", "Gamis"),
        ("Baju Tidur", "Baju Tidur"),
        ("Baju Sma", "Baju SMA"),
        ("Batik Sma", "Batik SMA"),
        ("Olahraga Sekolah", "Olahraga Sekolah"),
        ("Baju Sekolah", "Baju Sekolah"),
        ("Bra", "Bra"),
        ("Singlet", "Singlet"),
        ("Kaos Kaki", "Kaos Kaki"),
        ("Handuk", "Handuk"),
        ("Ciput", "Ciput"),
        ("Hoodie", "Hoodie"),
        ("Lekton", "Lekton"),
        ("Batik L. Panjang", "Batik Lengan Panjang"),
    ]

    nota = models.ForeignKey(Nota, on_delete=models.CASCADE, related_name="items")
    jenis = models.CharField(max_length=100, choices=JENIS_PAKAIAN)
    jumlah = models.PositiveIntegerField(default=1)
    catatan = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.get_jenis_display()} ({self.jumlah})"
