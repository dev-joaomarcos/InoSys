from django import forms
from django.utils import timezone

from .models import Material, Movimentacao


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["nome", "descricao", "unidade_medida", "quantidade_minima"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"].error_messages["required"] = "Informe o nome do material."
        self.fields["unidade_medida"].error_messages["required"] = "Informe a unidade (ex.: un, m², cx)."
        qm = self.fields["quantidade_minima"]
        qm.error_messages.update(required="Informe um número igual ou maior que zero.",
                                 invalid="Informe um número inteiro igual ou maior que zero.")

    def clean_nome(self):
        return self.cleaned_data["nome"].strip()

    def clean_unidade_medida(self):
        return self.cleaned_data["unidade_medida"].strip()


class MovimentacaoForm(forms.Form):
    tipo = forms.ChoiceField(choices=Movimentacao.TIPOS)
    material = forms.ModelChoiceField(queryset=Material.objects.none(),
                                      error_messages={"required": "Escolha o material.",
                                                      "invalid_choice": "Escolha um material ativo."})
    quantidade = forms.IntegerField(min_value=1, error_messages={
        "required": "Informe uma quantidade maior que zero.",
        "min_value": "Informe uma quantidade maior que zero.",
        "invalid": "Informe uma quantidade maior que zero."})
    data = forms.DateField(initial=timezone.localdate, error_messages={"required": "Informe a data.",
                                                                       "invalid": "Informe uma data válida."})
    motivo = forms.ChoiceField(choices=Movimentacao.MOTIVOS, required=False,
                               error_messages={"invalid_choice": "Escolha o motivo da saída."})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.objects.ativos().order_by("nome")  # só materiais ativos

    def clean(self):
        dados = super().clean()
        if dados.get("tipo") == Movimentacao.SAIDA and not dados.get("motivo"):
            self.add_error("motivo", "Escolha o motivo da saída.")
        if dados.get("tipo") == Movimentacao.ENTRADA:
            dados["motivo"] = ""  # motivo só existe em saída
        return dados
