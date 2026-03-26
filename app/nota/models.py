from django.db import models


class Pelanggan(models.Model):
    JNS_PLGGN = (
        ('umum', 'Umum'),
        ('lpk', 'LPK'),
        ('sekolah', 'Sekolah')
    )

    nama = models.CharField(max_length=100)
    alamat = models.CharField(max_length=200, blank=True, null=True)
    jenis_plggn = models.CharField(max_length=20, choices=JNS_PLGGN)

    def __str__(self):
        return self.nama


class Nota(models.Model):

    pelanggan = models.ForeignKey(
        Pelanggan,
        on_delete=models.CASCADE,
        related_name='notas'
    )

    berat = models.FloatField()

    JENIS = (
        ('cs', 'Cuci Setrika'),
        ('c', 'Cuci'),
        ('s', 'Setrika'),
    )

    LAYANAN = (
        ('reguler', 'Reguler'),
        ('express', 'Express'),
    )

    STATUS = [
        ('Belum', 'Belum Didata/Selesai'),
        ('Sudah', 'Sudah Didata'),
    ]

    jenis = models.CharField(max_length=20, choices=JENIS)
    layanan = models.CharField(max_length=20, choices=LAYANAN)
    status = models.CharField(max_length=50, choices=STATUS, default='Belum Didata/Selesai')
    harga = models.IntegerField()
    tgl = models.DateField()

    def __str__(self):
        return f"{self.pelanggan.nama} - {self.harga}"


class ItemPakaian(models.Model):

    JENIS_PAKAIAN = [
        ('Kaos L. Pendek', 'Kaos Lengan Pendek'),
        ('Kaos L. Panjang', 'Kaos Lengan Panjang'),
        ('Kemeja L. Pendek', 'Kemeja Lengan Pendek'),
        ('Kemeja L. Panjang', 'Kemeja Lengan Panjang'),
        ('Celana Panjang', 'Celana Panjang'),
        ('Celana Pendek', 'Celana Pendek'),
        ('Celana Dalam', 'Celana Dalam'),
        ('Kerudung', 'Kerudug'),
        ('Jaket', 'Jaket'),
        ('Sprei', 'Sprei'),
        ('Selimut', 'Selimut'),
        ('Sarung Bantal', 'Sarung Bantal'),
        ('Daster', 'Daster'),
        ('Sarung', 'Sarung'),
        ('Polo Osin', 'Polo Osin'),
        ('Kemeja Osin', 'Kemeja Osin'),
        ('Sajadah', 'Sajadah'),
        ('Training Osin', 'Training Osin'),
        ('Batik Osin', 'Batik Osin'),
        ('Koko Osin', 'Koko Osin'),
        ('Kupluk', 'Kupluk'),
        ('Dasi', 'Dasi'),
        ('Jas', 'Jas'),
        ('Kaos Osin', 'Kaos Osin'),
        ('Baju Koko', 'Baju Koko'),
        ('Gamis', 'Gamis'),
        ('Baju Tidur', 'Baju Tidur'),
        ('Baju Sma', 'Baju Sma'),
        ('Batik Sma', 'Batik Sma'),
        ('Olahraga Sekolah', 'Olahraga Sekolah'),
        ('Baju Sekolah', 'Baju Sekolah'),
        ('Bra', 'Bra'),
        ('Singlet', 'Singlet'),
        ('Kaos Kaki', 'Kaos Kaki'),
        ('Handuk', 'Handuk'),
        ('Ciput', 'Ciput'),
        ('Hoodie', 'Hoodie'),
    ]

    nota = models.ForeignKey(
        Nota,
        on_delete=models.CASCADE,
        related_name='items'
    )

    jenis = models.CharField(max_length=50, choices=JENIS_PAKAIAN)
    
    jumlah = models.PositiveIntegerField(default=1)
    catatan = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.get_jenis_display()} ({self.jumlah})"
