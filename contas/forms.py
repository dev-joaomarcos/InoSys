from django import forms
from django.core.validators import RegexValidator

from .models import Usuario


class UsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, validators=[RegexValidator(
        r"^[A-Za-z0-9.@+_-]+$", "Informe um usuário válido, sem espaços.")], error_messages={
        "required": "Informe um usuário válido, sem espaços."})

    class Meta:
        model = Usuario
        fields = ["nome", "username", "perfil"]
        error_messages = {"username": {"unique": "Já existe um usuário com esse nome de acesso."}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"].required = True
        self.fields["nome"].error_messages["required"] = "Informe o nome."
        self.fields["perfil"].error_messages.update(required="Escolha o perfil.", invalid_choice="Escolha o perfil.")
        if not self.instance.pk and not self.is_bound:
            self.initial["perfil"] = ""  # novo usuário: a lista começa em "Selecione…"

    def clean_nome(self):
        return self.cleaned_data["nome"].strip()

    def clean_username(self):
        usuario = self.cleaned_data["username"].strip()
        outros = Usuario.objects.filter(username=usuario).exclude(pk=self.instance.pk)
        if outros.exists():
            raise forms.ValidationError("Já existe um usuário com esse nome de acesso.")
        return usuario
