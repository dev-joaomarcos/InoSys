from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods

from contas.formatos import moeda, numero
from contas.htmx import eh_htmx, pagina_ou_trecho, salvo
from contas.logs import registrar_log
from contas.models import LogAcao
from contas.permissoes import FRETES, perfil_requerido

from .forms import EntregadorForm, EntregaForm
from .models import Entrega, Entregador
from .services import calcular_sugerido

POR_PAGINA = 20  # README: Paginator nativo, 20 itens por página
EVENTO_ENTREGAS, EVENTO_ENTREGADORES = "fretesAtualizados", "entregadoresAtualizados"


def _txt(valor):
    """Valor de campo como texto para o <input>: ponto decimal e data ISO, sem formatação local."""
    if valor is None:
        return ""
    return valor.isoformat() if hasattr(valor, "isoformat") else str(valor)


def _data(valor):
    """Data do filtro (AAAA-MM-DD); texto inválido é ignorado em vez de quebrar a tela."""
    try:
        return parse_date(valor or "")
    except ValueError:
        return None


# ------------------------------------------------------------------- entregas
def contexto_resumo():
    divergentes = Entrega.objects.filter(valor_cobrado__isnull=False).exclude(valor_cobrado=F("valor_sugerido"))
    contar = lambda status: Entrega.objects.filter(status=status).count()
    return {"pendentes": contar(Entrega.PENDENTE), "andamento": contar(Entrega.EM_ANDAMENTO),
            "concluidas": contar(Entrega.CONCLUIDA), "divergencias": divergentes.count()}


@perfil_requerido(*FRETES)
def entrega_lista(request):
    g = request.GET
    qs = Entrega.objects.select_related("entregador")
    if g.get("entregador", "").isdigit():
        qs = qs.filter(entregador_id=g["entregador"])
    if g.get("status") in dict(Entrega.STATUS):
        qs = qs.filter(status=g["status"])
    if _data(g.get("data_inicio")):
        qs = qs.filter(data__gte=_data(g["data_inicio"]))
    if _data(g.get("data_fim")):
        qs = qs.filter(data__lte=_data(g["data_fim"]))
    pagina = Paginator(qs.order_by("-data", "-pk"), POR_PAGINA).get_page(g.get("pagina"))
    contexto = {"page_obj": pagina, "entregadores_filtro": Entregador.objects.order_by(Lower("nome")),
                "f": {k: g.get(k, "") for k in ("entregador", "status", "data_inicio", "data_fim")}}
    if not eh_htmx(request):
        contexto.update(contexto_resumo())
    return pagina_ou_trecho(request, "fretes/entregas.html", "fretes/_lista_entregas.html", contexto)


@perfil_requerido(*FRETES)
def entrega_resumo(request):
    return render(request, "fretes/_resumo_fretes.html", contexto_resumo())


def _form_entrega(request, entrega=None):
    novo = entrega is None
    form = EntregaForm(request.POST if request.method == "POST" else None, instance=entrega)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        # O sugerido é recalculado ao criar ou ao mudar entregador/distância. Editar só o status ou o valor
        # cobrado não mexe nele: mudar o valor por km vale só para as próximas entregas.
        if novo or {"entregador", "distancia"} & set(form.changed_data):
            obj.valor_sugerido = calcular_sugerido(obj.distancia, obj.entregador.valor_por_km)
        if novo:
            obj.usuario = request.user
        obj.save()
        registrar_log(request.user, LogAcao.CRIACAO if novo else LogAcao.EDICAO)
        return salvo(EVENTO_ENTREGAS, "Entrega registrada." if novo else "Entrega atualizada.")
    contexto = {"form": form, "entrega": entrega, "acao": request.path,
                "valores": {c: _txt(form[c].value()) for c in ("data", "distancia", "valor_cobrado")}}
    if entrega:  # valor gravado na entrega; muda ao vivo se entregador ou distância forem alterados
        contexto.update(sugerido_texto=moeda(entrega.valor_sugerido), sugerido_iso=str(entrega.valor_sugerido))
    return render(request, "fretes/_form_entrega.html", contexto)


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entrega_nova(request):
    return _form_entrega(request)


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entrega_editar(request, pk):
    return _form_entrega(request, get_object_or_404(Entrega, pk=pk))


@perfil_requerido(*FRETES)
def valor_sugerido(request):
    """Trecho do #calculo-sugerido: distância × valor por km, enquanto a pessoa preenche o formulário."""
    contexto = {"formula": "Escolha o entregador e a distância", "texto": "—", "valor": ""}
    g = request.GET
    try:
        distancia = Decimal(g.get("distancia", "").replace(",", "."))
    except InvalidOperation:
        distancia = None
    entregador = Entregador.objects.filter(pk=g["entregador"]).first() if g.get("entregador", "").isdigit() else None
    if entregador and distancia is not None and distancia.is_finite() and distancia >= Decimal("0.1"):
        valor = calcular_sugerido(distancia, entregador.valor_por_km)
        contexto.update(formula=f"{numero(distancia, 1)} km × {moeda(entregador.valor_por_km)}/km",
                        texto=moeda(valor), valor=str(valor))
    return render(request, "fretes/_valor_sugerido.html", contexto)


# ---------------------------------------------------------------- entregadores
@perfil_requerido(*FRETES)
def entregador_lista(request):
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "ativo")  # sem parâmetro = só ativos; "" = todos
    qs = Entregador.objects.all()
    if busca:
        qs = qs.filter(Q(nome__icontains=busca) | Q(contato__icontains=busca))
    if status in (Entregador.ATIVO, Entregador.INATIVO):
        qs = qs.filter(status=status)
    pagina = Paginator(qs.order_by(Lower("nome"), "pk"), POR_PAGINA).get_page(request.GET.get("pagina"))
    return pagina_ou_trecho(request, "fretes/entregadores.html", "fretes/_lista_entregadores.html",
                            {"page_obj": pagina, "busca": busca, "status": status})


def _form_entregador(request, entregador=None):
    form = EntregadorForm(request.POST if request.method == "POST" else None, instance=entregador)
    if request.method == "POST" and form.is_valid():
        form.save()
        registrar_log(request.user, LogAcao.EDICAO if entregador else LogAcao.CRIACAO)
        return salvo(EVENTO_ENTREGADORES, "Entregador atualizado." if entregador else "Entregador cadastrado.")
    return render(request, "fretes/_form_entregador.html",
                  {"form": form, "entregador": entregador, "acao": request.path,
                   "valores": {"valor_por_km": _txt(form["valor_por_km"].value())}})


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entregador_novo(request):
    return _form_entregador(request)


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entregador_editar(request, pk):
    return _form_entregador(request, get_object_or_404(Entregador, pk=pk))


def _mudar_status(request, pk, ativar):
    entregador = get_object_or_404(Entregador, pk=pk)
    if request.method == "POST":
        entregador.status = Entregador.ATIVO if ativar else Entregador.INATIVO
        entregador.save(update_fields=["status"])
        registrar_log(request.user, LogAcao.EDICAO)
        return salvo(EVENTO_ENTREGADORES,
                     "Entregador reativado." if ativar else "Entregador desativado. O histórico foi mantido.")
    return render(request, "fretes/_form_status_entregador.html",
                  {"entregador": entregador, "desativar": not ativar, "acao": request.path})


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entregador_desativar(request, pk):
    return _mudar_status(request, pk, ativar=False)


@perfil_requerido(*FRETES)
@require_http_methods(["GET", "POST"])
def entregador_reativar(request, pk):
    return _mudar_status(request, pk, ativar=True)
