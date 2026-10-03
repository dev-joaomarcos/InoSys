from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from core.mixins import Criar, Editar, Excluir, Lista

from .forms import MovimentacaoForm, ProdutoEdicaoForm, ProdutoForm
from .models import Movimentacao, Produto

SITUACOES = [("Ok", "Ok"), ("Repor", "Repor"), ("Zerado", "Zerado")]


class ProdutoLista(Lista):
    queryset = Produto.objects.all()
    partial = "estoque/_produtos_tabela.html"
    titulo_lista, url_novo, rotulo_novo = "Produtos", "produto_novo", "Novo produto"
    campos_busca = ("nome", "sku")
    opcoes_status = SITUACOES
    ordenaveis = ("nome", "sku", "quantidade", "estoque_minimo")

    def filtrar_status(self, qs, st):
        if st == "Zerado":
            return qs.filter(quantidade__lte=0)
        if st == "Repor":
            return qs.filter(quantidade__gt=0, quantidade__lte=F("estoque_minimo"))
        if st == "Ok":
            return qs.filter(quantidade__gt=F("estoque_minimo"))
        return qs


class ProdutoCriar(Criar):
    model = Produto
    form_class = ProdutoForm
    titulo = "Novo produto"
    mensagem = "Produto cadastrado."
    success_url = reverse_lazy("produto_lista")

    def form_valid(self, form):
        with transaction.atomic():
            resposta = super().form_valid(form)
            if self.object.quantidade > 0:  # saldo inicial entra no histórico
                Movimentacao.objects.create(produto=self.object, tipo=Movimentacao.ENTRADA,
                                            quantidade=self.object.quantidade, observacao="Saldo inicial",
                                            usuario=self.request.user)
        return resposta


class ProdutoEditar(Editar):
    model = Produto
    form_class = ProdutoEdicaoForm
    titulo = "Editar produto"
    mensagem = "Produto atualizado."
    success_url = reverse_lazy("produto_lista")


class ProdutoExcluir(Excluir):
    model = Produto
    success_url = reverse_lazy("produto_lista")
    aviso = "O histórico de movimentações deste produto também será apagado."
    mensagem = "Produto excluído."


class MovimentacaoLista(Lista):
    queryset = Movimentacao.objects.select_related("produto", "usuario")
    partial = "estoque/_mov_tabela.html"
    titulo_lista = "Histórico de movimentações"
    campos_busca = ("produto__nome", "produto__sku", "observacao")
    campo_status = "tipo"
    opcoes_status = Movimentacao.TIPOS
    ordenaveis = ("data", "produto__nome", "tipo", "quantidade")


class MovimentacaoCriar(Criar):
    """Registra entrada (tipo=E) ou saída (tipo=S) e atualiza o saldo do produto."""
    model = Movimentacao
    form_class = MovimentacaoForm
    success_url = reverse_lazy("mov_lista")

    def get_produto(self):
        return get_object_or_404(Produto, pk=self.kwargs["pk"])

    def get_titulo(self):
        rotulo = "Entrada" if self.kwargs["tipo"] == Movimentacao.ENTRADA else "Saída"
        p = self.get_produto()
        return f"{rotulo} de {p.nome} (saldo: {p.quantidade:.2f} {p.unidade})"

    def form_valid(self, form):
        tipo, qtd = self.kwargs["tipo"], form.cleaned_data["quantidade"]
        with transaction.atomic():
            p = Produto.objects.select_for_update().get(pk=self.kwargs["pk"])
            if tipo == Movimentacao.SAIDA and qtd > p.quantidade:
                form.add_error("quantidade", f"Saldo insuficiente: há {p.quantidade:.2f} {p.unidade} em estoque.")
                return self.form_invalid(form)
            p.quantidade += qtd if tipo == Movimentacao.ENTRADA else -qtd
            p.save(update_fields=["quantidade"])
            form.instance.produto, form.instance.tipo, form.instance.usuario = p, tipo, self.request.user
            self.mensagem = "Movimentação registrada."
            return super().form_valid(form)
