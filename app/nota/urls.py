from django.urls import path
from . import views


app_name = 'nota'

urlpatterns = [
    #DASHBOARD
    path("", views.index, name="dashboard"), 
    path("data_nota/", views.data_nota, name="data_nota"),
    path("data_nota/edit/<int:id>/", views.nota_edit, name="nota_edit"),
    path("data_nota/delete/<int:id>/", views.nota_delete, name="nota_delete"),

]
