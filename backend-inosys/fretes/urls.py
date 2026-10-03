from django.urls import path

from . import views as v

urlpatterns = [
    path("", v.FreteLista.as_view(), name="frete_lista"),
    path("novo/", v.FreteCriar.as_view(), name="frete_novo"),
    path("<int:pk>/editar/", v.FreteEditar.as_view(), name="frete_editar"),
    path("<int:pk>/excluir/", v.FreteExcluir.as_view(), name="frete_excluir"),
    path("entregadores/", v.EntregadorLista.as_view(), name="entregador_lista"),
    path("entregadores/novo/", v.EntregadorCriar.as_view(), name="entregador_novo"),
    path("entregadores/<int:pk>/editar/", v.EntregadorEditar.as_view(), name="entregador_editar"),
    path("entregadores/<int:pk>/excluir/", v.EntregadorExcluir.as_view(), name="entregador_excluir"),
]
