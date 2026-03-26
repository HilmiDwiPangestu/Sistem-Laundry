from django.db import models

class ItemLaundry(models.Model):

    PILIHAN_PAKAIAN = [
        ('kaos_pendek', 'Kaos Lengan Pendek'),
        ('kaos_panjang', 'Kaos Lengan Panjang'),
        ('kemeja_pendek', 'Kemeja Lengan Pendek'),
        ('kemeja_panjang', 'Kemeja Lengan Panjang'),
        ('celana_pendek', 'Celana Pendek'),
        ('celana_panjang', 'Celana Panjang'),
        ('jaket', 'Jaket'),
        ('sweater', 'Sweater'),
        ('hoodie', 'Hoodie'),
        ('lainnya', 'Lainnya'),
    ]

    jenis_pakaian = models.CharField(max_length=50, choices=PILIHAN_PAKAIAN)
    jumlah = models.IntegerField(default=1)
    keterangan = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_jenis_pakaian_display()} - {self.jumlah}"
