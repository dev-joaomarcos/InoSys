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


class ApresentacaoView(TemplateView):
    """Landing page pública: apresenta o sistema e leva ao login."""
    template_name = "contas/apresentacao.html"


class SelecaoView(TemplateView):
    """Raiz do site. Quem está logado escolhe o módulo; quem não está vê a apresentação."""
    template_name = "contas/selecao.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return ApresentacaoView.as_view()(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
