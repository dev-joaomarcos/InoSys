from django.urls import path

from . import views as v

app_name = "estoque"

urlpatterns = [
    path("materiais/", v.material_lista, name="material_lista"),
    path("materiais/resumo/", v.material_resumo, name="material_resumo"),
    path("materiais/novo/", v.material_novo, name="material_novo"),
    path("materiais/<int:pk>/editar/", v.material_editar, name="material_editar"),
    path("materiais/<int:pk>/desativar/", v.material_desativar, name="material_desativar"),
    path("materiais/<int:pk>/reativar/", v.material_reativar, name="material_reativar"),
    path("movimentacoes/", v.movimentacao_lista, name="movimentacao_lista"),
    path("movimentacoes/nova/", v.movimentacao_nova, name="movimentacao_nova"),
]
