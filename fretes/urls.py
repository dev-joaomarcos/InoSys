from django.urls import path

from . import views as v

app_name = "fretes"

urlpatterns = [
    path("entregas/", v.entrega_lista, name="entrega_lista"),
    path("entregas/resumo/", v.entrega_resumo, name="entrega_resumo"),
    path("entregas/nova/", v.entrega_nova, name="entrega_nova"),
    path("entregas/valor-sugerido/", v.valor_sugerido, name="valor_sugerido"),
    path("entregas/<int:pk>/editar/", v.entrega_editar, name="entrega_editar"),
    path("entregadores/", v.entregador_lista, name="entregador_lista"),
    path("entregadores/novo/", v.entregador_novo, name="entregador_novo"),
    path("entregadores/<int:pk>/editar/", v.entregador_editar, name="entregador_editar"),
    path("entregadores/<int:pk>/desativar/", v.entregador_desativar, name="entregador_desativar"),
    path("entregadores/<int:pk>/reativar/", v.entregador_reativar, name="entregador_reativar"),
]
