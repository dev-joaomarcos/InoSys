from django.db.models import Count
from django.urls import reverse_lazy

from core.mixins import Criar, Editar, Excluir, Lista

from .forms import EntregadorForm, FreteForm
from .models import STATUS, Entregador, Frete


class FreteLista(Lista):
    queryset = Frete.objects.select_related("entregador")
    partial = "fretes/_fretes_tabela.html"
    titulo_lista, url_novo, rotulo_novo = "Fretes", "frete_novo", "Novo frete"
    campos_busca = ("codigo", "cliente", "origem", "destino", "entregador__nome")
    campo_status = "status"
    opcoes_status = STATUS
    ordenaveis = ("codigo", "cliente", "origem", "destino", "entregador__nome", "modal", "previsao", "status", "valor")


class FreteCriar(Criar):
    model, form_class, titulo = Frete, FreteForm, "Novo frete"
    mensagem = "Frete registrado."
    success_url = reverse_lazy("frete_lista")


class FreteEditar(Editar):
    model, form_class, titulo = Frete, FreteForm, "Editar frete"
    mensagem = "Frete atualizado."
    success_url = reverse_lazy("frete_lista")


class FreteExcluir(Excluir):
    model = Frete
    success_url = reverse_lazy("frete_lista")
    mensagem = "Frete excluído."


class EntregadorLista(Lista):
    queryset = Entregador.objects.annotate(n_fretes=Count("fretes"))
    partial = "fretes/_entregadores_tabela.html"
    titulo_lista, url_novo, rotulo_novo = "Entregadores", "entregador_novo", "Novo entregador"
    campos_busca = ("nome", "telefone", "veiculo")
    ordenaveis = ("nome", "telefone", "veiculo", "n_fretes")


class EntregadorCriar(Criar):
    model, form_class, titulo = Entregador, EntregadorForm, "Novo entregador"
    mensagem = "Entregador cadastrado."
    success_url = reverse_lazy("entregador_lista")


class EntregadorEditar(Editar):
    model, form_class, titulo = Entregador, EntregadorForm, "Editar entregador"
    mensagem = "Entregador atualizado."
    success_url = reverse_lazy("entregador_lista")


class EntregadorExcluir(Excluir):
    model = Entregador
    success_url = reverse_lazy("entregador_lista")
    aviso = "Entregadores com fretes registrados não podem ser excluídos."
    mensagem = "Entregador excluído."
