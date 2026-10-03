from django import forms


class EstiloForm(forms.ModelForm):
    """ModelForm que aplica a classe visual do painel em todos os campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "field w-full"
