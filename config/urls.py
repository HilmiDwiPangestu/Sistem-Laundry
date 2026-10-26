from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from app.user import views as user_views
from .pwa import service_worker

urlpatterns = [
    path("service-worker.js", service_worker, name="service_worker"),
    path("", user_views.landing_page, name="landing"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("login/redirect/", user_views.role_redirect, name="role_redirect"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Admin Center adalah panel utama admin. Django admin tetap tersedia sebagai
    # alat teknis cadangan di /system-admin/.
    path("admin-panel/", include("app.user.admin_urls")),
    path("system-admin/", admin.site.urls),

    # Seluruh area operasional karyawan dikelompokkan di /karyawan/ agar
    # terpisah jelas dari landing page publik dan Admin Center.
    path("karyawan/nota/", include("app.nota.urls")),
    path("karyawan/item/", include("app.item.urls")),
    path("karyawan/", include("app.user.urls")),
]
