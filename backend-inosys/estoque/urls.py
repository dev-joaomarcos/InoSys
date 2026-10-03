from django.urls import path

from . import views as v

urlpatterns = [
    path("", v.ProdutoLista.as_view(), name="produto_lista"),
    path("novo/", v.ProdutoCriar.as_view(), name="produto_novo"),
    path("<int:pk>/editar/", v.ProdutoEditar.as_view(), name="produto_editar"),
    path("<int:pk>/excluir/", v.ProdutoExcluir.as_view(), name="produto_excluir"),
    path("<int:pk>/entrada/", v.MovimentacaoCriar.as_view(), {"tipo": "E"}, name="entrada"),
    path("<int:pk>/saida/", v.MovimentacaoCriar.as_view(), {"tipo": "S"}, name="saida"),
    path("movimentacoes/", v.MovimentacaoLista.as_view(), name="mov_lista"),
]
