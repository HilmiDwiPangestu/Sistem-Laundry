from django.urls import path
from . import views


app_name = 'user'

urlpatterns = [
    #DASHBOARD
    path("", views.index, name="user_index"),
    path("tambah_item/<int:nota_id>/", views.tambah_item, name="tambah_item"),
    path("tambah_nota/", views.tambahNota, name="tambah_nota"),
    path("buat_nota/<int:pelanggan_id>/", views.buatNota, name="buat_nota"),
    path("pelanggan_baru/", views.pelangganBaru, name="pelanggan_baru"),
    path('nota/hapus/<int:nota_id>/', views.hapusNota, name='hapus_nota'),
    path('nota/selesai/<int:nota_id>/', views.selesaiItem, name='nota_selesai'),
    # path("data_nota/", views.data_nota, name="data_nota"),
]
