from django.shortcuts import redirect


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
                return redirect("contas:trocar_senha")
