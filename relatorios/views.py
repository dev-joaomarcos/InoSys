from django.db.models.functions import Lower
from django.shortcuts import render
from django.utils.dateparse import parse_date

from contas.formatos import moeda
from contas.htmx import eh_htmx
from contas.permissoes import GESTAO, perfil_requerido
from estoque.models import Material
from fretes.models import Entrega, Entregador

from . import services


def _data(valor):
    try:
        return parse_date(valor or "")
    except ValueError:
        return None


def _datas(g):
    """Período do filtro. Sem parâmetro = últimos 30 dias; parâmetro vazio ou inválido = sem limite."""
    padrao_ini, padrao_fim = services.periodo_padrao()
    ini = _data(g["data_inicio"]) if "data_inicio" in g else padrao_ini
    fim = _data(g["data_fim"]) if "data_fim" in g else padrao_fim
    return ini, fim


def _contexto_movimentacoes(g):
    ini, fim = _datas(g)
    material = g.get("material", "") if g.get("material", "").isdigit() else ""
    rel = services.relatorio_movimentacoes(material or None, ini, fim)
    return {"mov": rel, "materiais": Material.objects.order_by(Lower("nome")),
            "fm": {"material": material, "data_inicio": ini, "data_fim": fim}}


def _contexto_fretes(g):
    ini, fim = _datas(g)
    entregador = g.get("entregador", "") if g.get("entregador", "").isdigit() else ""
    status = g.get("status", "") if g.get("status") in dict(Entrega.STATUS) else ""
    so_div = g.get("so_divergencias") == "1"
    rel = services.relatorio_fretes(entregador or None, status, ini, fim, so_div)
    return {"fre": rel, "entregadores": Entregador.objects.order_by(Lower("nome")), "status_opcoes": Entrega.STATUS,
            "ff": {"entregador": entregador, "status": status, "so_divergencias": so_div,
                   "data_inicio": ini, "data_fim": fim}}


def _pagina_completa(request, aba, g_mov, g_fre):
    contexto = {**_contexto_movimentacoes(g_mov), **_contexto_fretes(g_fre), "aba": aba}
    return render(request, "relatorios/relatorios.html", contexto)


@perfil_requerido(*GESTAO)
def visao_geral(request):
    r = services.resumo_geral()
    r["aria_grafico"] = "Sugerido e cobrado por entregador. " + " ".join(
        f"{x['nome']}: {moeda(x['sugerido'])} e {moeda(x['cobrado'])}." for x in r["grafico"])
    r["notas_grafico"] = [
        {"nome": x["nome"], "valor": moeda(abs(x["diferenca"])), "mais": x["diferenca"] > 0}
        for x in r["grafico"] if x["diferenca"] != 0]
    return render(request, "relatorios/visao_geral.html", r)


@perfil_requerido(*GESTAO)
def relatorios(request):
    return _pagina_completa(request, "movimentacoes", {}, {})


@perfil_requerido(*GESTAO)
def relatorio_movimentacoes(request):
    if eh_htmx(request):
        return render(request, "relatorios/_relatorio_movimentacoes.html", _contexto_movimentacoes(request.GET))
    return _pagina_completa(request, "movimentacoes", request.GET, {})  # endereço copiado do navegador


@perfil_requerido(*GESTAO)
def relatorio_fretes(request):
    if eh_htmx(request):
        return render(request, "relatorios/_relatorio_fretes.html", _contexto_fretes(request.GET))
    return _pagina_completa(request, "fretes", {}, request.GET)
