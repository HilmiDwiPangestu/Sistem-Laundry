from django.urls import path
from . import views


app_name = 'item'

urlpatterns = [
    #DASHBOARD
    path("", views.data_item, name="data_item"), 
    path("list-item/<int:nota_id>/", views.detailItem, name="detail_item"), 
    path('laporan/bulanan/', views.laporan_bulanan, name='laporan_bulanan'),
    path('laporan/tanggal/<str:tgl>/', views.laporan_detail_tanggal, name='laporan_detail_tanggal'),
]
