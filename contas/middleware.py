from django.shortcuts import redirect
from django.urls import reverse

from .htmx import ir_para


class TrocaSenhaObrigatoriaMiddleware:
    """Quem entrou com senha temporária só consegue trocar a senha ou sair."""
    LIBERADAS = {"contas:trocar_senha", "contas:logout"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        usuario = request.user
        if usuario.is_authenticated and getattr(usuario, "senha_temporaria", False):
            if request.resolver_match and request.resolver_match.view_name not in self.LIBERADAS:
                if request.headers.get("HX-Request") == "true":  # a página inteira vai para a troca de senha
                    return ir_para(reverse("contas:trocar_senha"), status=403)
                return redirect("contas:trocar_senha")
