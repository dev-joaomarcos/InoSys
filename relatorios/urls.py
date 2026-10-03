from django.urls import path

from . import views

app_name = "relatorios"

urlpatterns = [
    path("visao-geral/", views.visao_geral, name="visao_geral"),
    path("relatorios/", views.relatorios, name="relatorios"),
    path("relatorios/movimentacoes/", views.relatorio_movimentacoes, name="relatorio_movimentacoes"),
    path("relatorios/fretes/", views.relatorio_fretes, name="relatorio_fretes"),
]
