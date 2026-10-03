from django import forms

from core.forms import EstiloForm

from .models import Movimentacao, Produto


class ProdutoForm(EstiloForm):
    class Meta:
        model = Produto
        fields = ["nome", "sku", "unidade", "quantidade", "estoque_minimo"]
        labels = {"quantidade": "Quantidade inicial"}


class ProdutoEdicaoForm(EstiloForm):
    """O saldo só muda por movimentações, para o histórico nunca ficar desencontrado."""
    class Meta:
        model = Produto
        fields = ["nome", "sku", "unidade", "estoque_minimo"]


class MovimentacaoForm(EstiloForm):
    class Meta:
        model = Movimentacao
        fields = ["quantidade", "data", "observacao"]
        widgets = {"data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}
