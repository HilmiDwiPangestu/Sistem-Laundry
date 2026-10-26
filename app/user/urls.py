from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "user"

urlpatterns = [
    path("", views.index, name="user_index"),
    path("transaksi/baru/", views.transaksi_baru, name="transaksi_baru"),
    path("transaksi/<int:nota_id>/", views.nota_detail, name="nota_detail"),
    path("harga-layanan/", views.harga_layanan, name="harga_layanan"),
    # Legacy paths redirect to the canonical Admin Center URLs.
    path("control-center/", RedirectView.as_view(pattern_name="adminpanel:control_center", permanent=False), name="control_center"),
    path("control-center/test-struk/", RedirectView.as_view(pattern_name="adminpanel:receipt_test", permanent=False, query_string=True), name="receipt_test"),
    path("transaksi/<int:nota_id>/struk/", views.nota_receipt, name="nota_receipt"),
    path("pelanggan/", views.pelanggan_list, name="pelanggan_list"),
    path("pelanggan/baru/", views.pelangganBaru, name="pelanggan_baru"),
    path("pelanggan/<int:pelanggan_id>/edit/", views.pelanggan_edit, name="pelanggan_edit"),
    path("pelanggan/<int:pelanggan_id>/nota/baru/", views.buatNota, name="buat_nota"),
    path("tambah_nota/", views.tambahNota, name="tambah_nota"),
    path("nota/<int:nota_id>/item/", views.tambah_item, name="tambah_item"),
    path("nota/<int:nota_id>/item/<int:item_id>/jumlah/", views.ubah_jumlah_item, name="ubah_jumlah_item"),
    path("nota/<int:nota_id>/item/<int:item_id>/hapus/", views.hapus_item, name="hapus_item"),
    path("nota/<int:nota_id>/hapus/", views.hapusNota, name="hapus_nota"),
    path("nota/<int:nota_id>/status/", views.selesaiItem, name="nota_selesai"),
]
