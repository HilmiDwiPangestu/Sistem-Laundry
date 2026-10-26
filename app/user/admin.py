from django.contrib import admin
from .models import LandingPageContent


@admin.register(LandingPageContent)
class LandingPageContentAdmin(admin.ModelAdmin):
    list_display = ("hero_title", "aktif", "tampilkan_harga", "updated_at")
