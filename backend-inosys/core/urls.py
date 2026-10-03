from django.urls import path

from . import views

urlpatterns = [
    path("", views.Geral.as_view(), name="geral"),
    path("busca/", views.Busca.as_view(), name="busca"),
]
