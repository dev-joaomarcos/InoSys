from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render
from django.utils.cache import add_never_cache_headers
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods

from .forms import UsuarioForm
from .gestao import anonimizar_usuario, gerar_senha_temporaria
from .htmx import eh_htmx, gatilho, pagina_ou_trecho, salvo
from .logs import registrar_log
from .models import LogAcao, PerfilUsuario, Usuario
from .permissoes import ADMINISTRACAO, perfil_requerido

POR_PAGINA = 20  # README: Paginator nativo, 20 itens por página
EVENTO = "usuariosAtualizados"
AJUDA_PERFIL = {
    "estoque": "Acessa só o módulo de estoque.",
    "fretes": "Acessa só o módulo de fretes.",
    "gestor": "Acessa estoque, fretes, visão geral e relatórios.",
    "admin": "Acesso completo, incluindo usuários, log de ações e anonimização.",
}


def _data(valor):
    try:
        return parse_date(valor or "")
    except ValueError:
        return None


def _editavel(pk):
    """Usuário anonimizado não volta: não edita, não ganha senha, não reativa."""
    return get_object_or_404(Usuario, pk=pk, anonimizado=False)


# ------------------------------------------------------------------- usuários
@perfil_requerido(*ADMINISTRACAO)
def usuario_lista(request):
    busca = request.GET.get("busca", "").strip()
    perfil = request.GET.get("perfil", "")
    status = request.GET.get("status", "ativo")  # sem parâmetro = só ativos; "" = todos
    qs = Usuario.objects.all()
    if busca:
        qs = qs.filter(Q(nome__icontains=busca) | Q(username__icontains=busca))
    if perfil in PerfilUsuario.values:
        qs = qs.filter(perfil=perfil)
    if status == "ativo":
        qs = qs.filter(ativo=True)
    elif status == "inativo":
        qs = qs.filter(ativo=False)
    pagina = Paginator(qs.order_by(Lower("nome"), "pk"), POR_PAGINA).get_page(request.GET.get("pagina"))
    return pagina_ou_trecho(request, "contas/usuarios.html", "contas/_lista_usuarios.html",
                            {"page_obj": pagina, "busca": busca, "perfil": perfil, "status": status,
                             "perfis": PerfilUsuario.choices})


def _form_usuario(request, usuario=None):
    form = UsuarioForm(request.POST if request.method == "POST" else None, instance=usuario)
    if request.method == "POST" and form.is_valid():
        if usuario and usuario == request.user and form.cleaned_data["perfil"] != PerfilUsuario.ADMIN:
            form.add_error("perfil", "Você não pode tirar o seu próprio perfil de administrador.")
        else:
            if usuario:
                form.save()
                registrar_log(request.user, LogAcao.EDICAO)
                return salvo(EVENTO, "Usuário atualizado.")
            senha = gerar_senha_temporaria()
            novo = form.save(commit=False)
            novo.set_password(senha)  # a senha só existe em texto nesta resposta
            novo.senha_temporaria = True
            novo.save()
            registrar_log(request.user, LogAcao.CRIACAO)
            resposta = render(request, "contas/_senha_temporaria.html",
                              {"usuario": novo, "senha": senha, "titulo": "Usuário cadastrado"})
            add_never_cache_headers(resposta)
            return gatilho(resposta, EVENTO)
    perfil_atual = str(form["perfil"].value() or "")
    return render(request, "contas/_form_usuario.html",
                  {"form": form, "usuario": usuario, "acao": request.path, "perfis": PerfilUsuario.choices,
                   "ajuda_perfil": AJUDA_PERFIL.get(perfil_atual, "Define quais módulos a pessoa enxerga.")})


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_novo(request):
    return _form_usuario(request)


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_editar(request, pk):
    return _form_usuario(request, _editavel(pk))


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_nova_senha(request, pk):
    usuario = _editavel(pk)
    if request.method == "POST":
        if usuario == request.user:
            return render(request, "contas/_form_nova_senha.html", {
                "usuario": usuario, "acao": request.path, "erro": "Para trocar a sua própria senha, use a tela de troca de senha."})
        senha = gerar_senha_temporaria()
        usuario.set_password(senha)  # a senha antiga deixa de valer e as sessões abertas caem
        usuario.senha_temporaria = True
        usuario.save(update_fields=["password", "senha_temporaria"])
        registrar_log(request.user, LogAcao.EDICAO)
        resposta = render(request, "contas/_senha_temporaria.html",
                          {"usuario": usuario, "senha": senha, "titulo": "Nova senha temporária"})
        add_never_cache_headers(resposta)
        return gatilho(resposta, EVENTO)
    return render(request, "contas/_form_nova_senha.html", {"usuario": usuario, "acao": request.path})


def _mudar_status(request, pk, ativar):
    usuario = _editavel(pk)
    erro = ""
    if request.method == "POST":
        if not ativar and usuario == request.user:
            erro = "Você não pode desativar o seu próprio acesso."
        else:
            usuario.ativo = ativar
            usuario.save(update_fields=["ativo"])
            registrar_log(request.user, LogAcao.EDICAO)
            return salvo(EVENTO, "Acesso reativado." if ativar else "Acesso desativado.")
    return render(request, "contas/_form_status_usuario.html",
                  {"usuario": usuario, "desativar": not ativar, "acao": request.path, "erro": erro})


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_desativar(request, pk):
    return _mudar_status(request, pk, ativar=False)


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_reativar(request, pk):
    return _mudar_status(request, pk, ativar=True)


@perfil_requerido(*ADMINISTRACAO)
@require_http_methods(["GET", "POST"])
def usuario_anonimizar(request, pk):
    usuario = _editavel(pk)
    erro = ""
    if request.method == "POST":
        if usuario == request.user:
            erro = "Você não pode anonimizar o seu próprio usuário."
        elif request.POST.get("confirmacao") != "1":
            erro = "Marque a confirmação para anonimizar."
        else:
            anonimizar_usuario(usuario)
            registrar_log(request.user, LogAcao.EDICAO)
            return salvo(EVENTO, "Dados anonimizados.")
    return render(request, "contas/_form_anonimizar.html", {"usuario": usuario, "acao": request.path, "erro": erro})


# ------------------------------------------------------------------------ log
@perfil_requerido(*ADMINISTRACAO)
def log_lista(request):
    g = request.GET
    qs = LogAcao.objects.all()
    if g.get("usuario", "").isdigit():
        qs = qs.filter(usuario_id=g["usuario"])
    if g.get("acao") in dict(LogAcao.ACOES):
        qs = qs.filter(acao=g["acao"])
    if _data(g.get("data_inicio")):
        qs = qs.filter(data_hora__date__gte=_data(g["data_inicio"]))
    if _data(g.get("data_fim")):
        qs = qs.filter(data_hora__date__lte=_data(g["data_fim"]))
    pagina = Paginator(qs.order_by("-data_hora", "-pk"), POR_PAGINA).get_page(g.get("pagina"))
    return pagina_ou_trecho(request, "contas/log.html", "contas/_lista_log.html", {
        "page_obj": pagina, "usuarios_filtro": Usuario.objects.order_by(Lower("nome")), "acoes": LogAcao.ACOES,
        "f": {k: g.get(k, "") for k in ("usuario", "acao", "data_inicio", "data_fim")}})
