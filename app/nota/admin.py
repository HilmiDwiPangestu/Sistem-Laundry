from django.contrib import admin
from .models import Nota, Pelanggan, ItemPakaian

# Register your models here.
admin.site.register(Nota)
admin.site.register(Pelanggan)
admin.site.register(ItemPakaian)