from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .logs import registrar_log
from .models import LogAcao


class LoginView(auth_views.LoginView):
    template_name = "contas/login.html"
    redirect_authenticated_user = True


class TrocarSenhaView(LoginRequiredMixin, auth_views.PasswordChangeView):
    """Campos old_password / new_password1 / new_password2, como no PasswordChangeForm."""
    template_name = "contas/troca_senha.html"
    success_url = reverse_lazy("contas:selecao")

    def form_valid(self, form):
        resposta = super().form_valid(form)
        usuario = form.user
        if usuario.senha_temporaria:
            usuario.senha_temporaria = False
            usuario.save(update_fields=["senha_temporaria"])
        registrar_log(usuario, LogAcao.EDICAO)
        return resposta


class SelecaoView(LoginRequiredMixin, TemplateView):
    template_name = "contas/selecao.html"
