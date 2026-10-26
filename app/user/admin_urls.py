from django.urls import path
from . import admin_views
from . import views as user_views

app_name = "adminpanel"

urlpatterns = [
    path("", admin_views.dashboard, name="dashboard"),
    # Admin-facing aliases for legacy control-center views. The views retain
    # their admin_required guard, while the canonical URL stays under /admin-panel/.
    path("control-center/", user_views.control_center, name="control_center"),
    path("control-center/test-struk/", user_views.receipt_test, name="receipt_test"),
    path("monitor-nota/", admin_views.note_monitor, name="note_monitor"),
    path("monitor-nota/data/", admin_views.note_monitor_data, name="note_monitor_data"),
    path("operasional/", admin_views.operations, name="operations"),
    path("operasional/nota/", admin_views.admin_notas, name="notas"),
    path("operasional/nota/baru/", admin_views.admin_nota_create, name="nota_create"),
    path("operasional/nota/<int:nota_id>/", admin_views.admin_nota_detail, name="nota_detail"),
    path("operasional/nota/<int:nota_id>/edit/", admin_views.admin_nota_edit, name="nota_edit"),
    path("operasional/nota/<int:nota_id>/status/", admin_views.admin_nota_status, name="nota_status"),
    path("operasional/nota/<int:nota_id>/hapus/", admin_views.admin_nota_delete, name="nota_delete"),
    path("operasional/pelanggan/", admin_views.admin_customers, name="customers"),
    path("operasional/pelanggan/tambah/", admin_views.admin_customer_create, name="customer_create"),
    path("operasional/pelanggan/<int:pelanggan_id>/edit/", admin_views.admin_customer_edit, name="customer_edit"),
    path("laporan/", admin_views.reports, name="reports"),
    path("laporan/download/", admin_views.report_download, name="report_download"),
    path("laporan/download/pdf/", admin_views.report_pdf_download, name="report_pdf_download"),
    path("laporan/tanggal/<str:tgl>/", admin_views.report_detail, name="report_detail"),
    path("laporan/tanggal/<str:tgl>/download/", admin_views.report_daily_download, name="report_daily_download"),
    path("laporan/tanggal/<str:tgl>/download/pdf/", admin_views.report_daily_pdf_download, name="report_daily_pdf_download"),
    path("landing-page/", admin_views.landing_editor, name="landing"),
    path("karyawan/", admin_views.employees, name="employees"),
    path("karyawan/tambah/", admin_views.employee_create, name="employee_create"),
    path("karyawan/<int:user_id>/edit/", admin_views.employee_edit, name="employee_edit"),
    path("karyawan/<int:user_id>/status/", admin_views.employee_toggle, name="employee_toggle"),
    path("pengaturan/", admin_views.settings_center, name="settings"),
]
