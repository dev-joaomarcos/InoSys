from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

# RNF05: perfis liberados em cada módulo.
ESTOQUE = ("estoque", "gestor", "admin")
FRETES = ("fretes", "gestor", "admin")
GESTAO = ("gestor", "admin")
ADMINISTRACAO = ("admin",)


def perfil_requerido(*perfis):
    """Para views de função: @perfil_requerido(*ESTOQUE)."""
    def decorador(view):
        @wraps(view)
        def interna(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
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
