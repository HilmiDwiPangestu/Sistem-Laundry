from django.urls import path
from . import views

app_name = "nota"

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("data/", views.data_nota, name="data_nota"),
    path("<int:id>/edit/", views.nota_edit, name="nota_edit"),
    path("<int:id>/hapus/", views.nota_delete, name="nota_delete"),
]
