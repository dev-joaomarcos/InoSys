import json

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods

from contas.logs import registrar_log
from contas.models import LogAcao
from contas.permissoes import ESTOQUE, perfil_requerido

from .forms import MaterialForm, MovimentacaoForm
from .models import Material, Movimentacao
from .services import registrar_movimentacao

POR_PAGINA = 20  # README: Paginator nativo, 20 itens por página


def eh_htmx(request):
    """Pedido do htmx que quer só o trecho. Ao voltar no histórico do navegador, vai a página inteira."""
    return request.headers.get("HX-Request") == "true" and request.headers.get("HX-History-Restore-Request") != "true"


def pagina_ou_trecho(request, pagina, trecho, contexto):
    resposta = render(request, trecho if eh_htmx(request) else pagina, contexto)
    patch_vary_headers(resposta, ["HX-Request"])
    return resposta


def salvo(mensagem):
    """204 + HX-Trigger: o modal fecha, as listas recarregam e aparece o aviso."""
    resposta = HttpResponse(status=204)
    resposta["HX-Trigger"] = json.dumps({"estoqueAtualizado": {"mensagem": mensagem}})  # ASCII puro (\uXXXX)
    return resposta


# ------------------------------------------------------------------ materiais
def contexto_resumo():
    baixos = list(Material.objects.baixos().order_by(Lower("nome")))
    return {"baixos": baixos, "qtd_baixo": len(baixos),
            "qtd_ativos": Material.objects.ativos().count(),
            "qtd_inativos": Material.objects.filter(status=Material.INATIVO).count()}


@perfil_requerido(*ESTOQUE)
def material_lista(request):
    busca = request.GET.get("busca", "").strip()
    situacao = request.GET.get("situacao", "")
    status = request.GET.get("status", "ativo")  # sem parâmetro = só ativos; "" = todos
    qs = Material.objects.all()
    if busca:
        qs = qs.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if status in (Material.ATIVO, Material.INATIVO):
        qs = qs.filter(status=status)
    if situacao == "baixo":
        qs = qs.baixos()
    elif situacao == "normal":
        qs = qs.ativos().exclude(qtd_atual__lt=F("quantidade_minima"))
    pagina = Paginator(qs.order_by(Lower("nome"), "pk"), POR_PAGINA).get_page(request.GET.get("pagina"))
    contexto = {"page_obj": pagina, "busca": busca, "situacao": situacao, "status": status}
    if not eh_htmx(request):
        contexto.update(contexto_resumo())
    return pagina_ou_trecho(request, "estoque/materiais.html", "estoque/_lista_materiais.html", contexto)


@perfil_requerido(*ESTOQUE)
def material_resumo(request):
    return render(request, "estoque/_resumo_estoque.html", contexto_resumo())


def _form_material(request, material=None):
    form = MaterialForm(request.POST if request.method == "POST" else None, instance=material)
    if request.method == "POST" and form.is_valid():
        form.save()
        registrar_log(request.user, LogAcao.EDICAO if material else LogAcao.CRIACAO)
        return salvo("Material atualizado." if material else "Material cadastrado com saldo 0.")
    return render(request, "estoque/_form_material.html", {"form": form, "material": material, "acao": request.path})


@perfil_requerido(*ESTOQUE)
@require_http_methods(["GET", "POST"])
def material_novo(request):
    return _form_material(request)


@perfil_requerido(*ESTOQUE)
@require_http_methods(["GET", "POST"])
def material_editar(request, pk):
    return _form_material(request, get_object_or_404(Material, pk=pk))


def _mudar_status(request, pk, ativar):
    material = get_object_or_404(Material, pk=pk)
    if request.method == "POST":
        material.status = Material.ATIVO if ativar else Material.INATIVO
        material.save(update_fields=["status"])
        registrar_log(request.user, LogAcao.EDICAO)
        return salvo("Material reativado." if ativar else "Material desativado. O histórico foi mantido.")
    return render(request, "estoque/_form_status_material.html",
                  {"material": material, "desativar": not ativar, "acao": request.path})


@perfil_requerido(*ESTOQUE)
@require_http_methods(["GET", "POST"])
def material_desativar(request, pk):
    return _mudar_status(request, pk, ativar=False)


@perfil_requerido(*ESTOQUE)
@require_http_methods(["GET", "POST"])
def material_reativar(request, pk):
    return _mudar_status(request, pk, ativar=True)


# -------------------------------------------------------------- movimentações
def _data(valor):
    """Data do filtro (AAAA-MM-DD); texto inválido é ignorado em vez de quebrar a tela."""
    try:
        return parse_date(valor or "")
    except ValueError:
        return None


@perfil_requerido(*ESTOQUE)
def movimentacao_lista(request):
    g = request.GET
    qs = Movimentacao.objects.select_related("material", "usuario")
    if g.get("material", "").isdigit():
        qs = qs.filter(material_id=g["material"])
    if g.get("tipo") in (Movimentacao.ENTRADA, Movimentacao.SAIDA):
        qs = qs.filter(tipo=g["tipo"])
    if _data(g.get("data_inicio")):
        qs = qs.filter(data__gte=_data(g["data_inicio"]))
    if _data(g.get("data_fim")):
        qs = qs.filter(data__lte=_data(g["data_fim"]))
    pagina = Paginator(qs.order_by("-data", "-pk"), POR_PAGINA).get_page(g.get("pagina"))
    contexto = {"page_obj": pagina, "materiais": Material.objects.order_by(Lower("nome")),
                "f": {k: g.get(k, "") for k in ("material", "tipo", "data_inicio", "data_fim")}}
    return pagina_ou_trecho(request, "estoque/movimentacoes.html", "estoque/_lista_movimentacoes.html", contexto)


@perfil_requerido(*ESTOQUE)
@require_http_methods(["GET", "POST"])
def movimentacao_nova(request):
    if request.method == "POST":
        valores = request.POST
        form = MovimentacaoForm(valores)
        if form.is_valid():
            d = form.cleaned_data
            try:
                registrar_movimentacao(request.user, d["material"], d["tipo"], d["quantidade"], d["data"], d["motivo"])
            except ValidationError as erro:
                form.add_error("quantidade" if "Saldo" in erro.messages[0] else "material", erro.messages[0])
            else:
                rotulo = "Saída" if d["tipo"] == Movimentacao.SAIDA else "Entrada"
                return salvo(f"{rotulo} de {d['quantidade']} {d['material'].unidade_medida} registrada.")
    else:
        tipo = request.GET.get("tipo")
        valores = {"tipo": tipo if tipo in ("entrada", "saida") else "entrada",
                   "material": request.GET.get("material", ""), "data": timezone.localdate().isoformat()}
        form = MovimentacaoForm()
    return render(request, "estoque/_form_movimentacao.html",
                  {"form": form, "v": valores, "materiais": form.fields["material"].queryset,
                   "motivos": Movimentacao.MOTIVOS})
