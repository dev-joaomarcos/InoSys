from functools import wraps
from urllib.parse import urlsplit

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .htmx import ir_para

# RNF05: perfis liberados em cada módulo.
ESTOQUE = ("estoque", "gestor", "admin")
FRETES = ("fretes", "gestor", "admin")
GESTAO = ("gestor", "admin")
ADMINISTRACAO = ("admin",)


def pedir_login(request):
    """Manda para o login quem não está autenticado (ou teve a sessão expirada).
    Pedido do htmx: a página inteira vai para o login e volta depois para a tela em que a pessoa estava,
    em vez de a tela de login aparecer dentro de um modal ou card."""
    if request.headers.get("HX-Request") == "true":
        atual = urlsplit(request.headers.get("HX-Current-URL", ""))
        voltar = atual.path + ("?" + atual.query if atual.query else "") if atual.path else "/"
        return ir_para(redirect_to_login(voltar).url, status=401)
    return redirect_to_login(request.get_full_path())


def perfil_requerido(*perfis):
    """Para views de função: @perfil_requerido(*ESTOQUE)."""
    def decorador(view):
        @wraps(view)
        def interna(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return pedir_login(request)
            if request.user.perfil not in perfis:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return interna
    return decorador


class PerfilRequeridoMixin(LoginRequiredMixin):
    """Para views de classe: defina `perfis = ESTOQUE`, por exemplo."""
    perfis = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.perfil not in self.perfis:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
