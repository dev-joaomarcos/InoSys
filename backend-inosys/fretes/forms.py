from django import forms

from core.forms import EstiloForm

from .models import Entregador, Frete


class FreteForm(EstiloForm):
    class Meta:
        model = Frete
        fields = ["cliente", "origem", "destino", "entregador", "modal", "previsao", "status", "valor", "observacao"]
        widgets = {"previsao": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class EntregadorForm(EstiloForm):
    class Meta:
        model = Entregador
        fields = ["nome", "telefone", "veiculo"]
