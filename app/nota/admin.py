from django.contrib import admin

from .models import HargaLayanan, ItemPakaian, Nota, Pelanggan, PengaturanLaundry


@admin.register(Pelanggan)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ("nama", "jenis_plggn", "alamat")
    search_fields = ("nama", "alamat")
    list_filter = ("jenis_plggn",)


@admin.register(HargaLayanan)
class HargaLayananAdmin(admin.ModelAdmin):
    list_display = ("nama", "kode", "harga_per_kg", "updated_at")
    ordering = ("urutan", "id")
    readonly_fields = ("kode", "nama", "urutan", "updated_at")


@admin.register(PengaturanLaundry)
class PengaturanLaundryAdmin(admin.ModelAdmin):
    list_display = ("nama_usaha", "lebar_kertas", "telepon", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not PengaturanLaundry.objects.exists()


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pelanggan",
        "tgl",
        "jenis",
        "layanan",
        "berat",
        "harga_per_kg",
        "harga",
        "status",
    )
    list_select_related = ("pelanggan",)
    list_filter = ("status", "jenis", "layanan", "tgl")
    search_fields = ("pelanggan__nama",)


@admin.register(ItemPakaian)
class ItemPakaianAdmin(admin.ModelAdmin):
    list_display = ("nota", "jenis", "jumlah", "catatan")
    search_fields = ("nota__pelanggan__nama", "jenis", "catatan")


admin.site.site_header = "Sani Laundry - Administrasi Sistem"
admin.site.site_title = "Sani Laundry"
admin.site.index_title = "Pengelolaan data sistem"
