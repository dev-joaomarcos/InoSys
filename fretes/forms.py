from decimal import Decimal

from django import forms
from django.db.models import Q

from .models import Entrega, Entregador


class EntregadorForm(forms.ModelForm):
    valor_por_km = forms.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0.01"), error_messages={
        "required": "Informe um valor maior que zero.", "invalid": "Informe um valor maior que zero.",
        "min_value": "Informe um valor maior que zero."})

    class Meta:
        model = Entregador
        fields = ["nome", "contato", "valor_por_km"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"].error_messages["required"] = "Informe o nome do entregador."

    def clean_nome(self):
        return self.cleaned_data["nome"].strip()


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["entregador", "data", "destino", "distancia", "valor_cobrado", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # só entregadores ativos; na edição, o entregador atual continua na lista mesmo se foi desativado
        filtro = Q(status=Entregador.ATIVO)
        if self.instance.pk:
            filtro |= Q(pk=self.instance.entregador_id)
        self.fields["entregador"].queryset = Entregador.objects.filter(filtro).order_by("nome")
        msgs = {"entregador": "Escolha o entregador.", "data": "Informe a data.", "destino": "Informe o destino.",
                "distancia": "Informe a distância em km."}
        for campo, texto in msgs.items():
            self.fields[campo].error_messages["required"] = texto
            self.fields[campo].error_messages["invalid_choice"] = texto
        self.fields["valor_cobrado"].error_messages["invalid"] = "Informe um valor igual ou maior que zero."

    def clean_destino(self):
        return self.cleaned_data["destino"].strip()
