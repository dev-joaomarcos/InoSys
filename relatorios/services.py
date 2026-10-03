"""Agregações dos dois módulos. O app `relatorios` é o único que importa estoque e fretes (README)."""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Lower
from django.utils import timezone

from estoque.models import Material, Movimentacao
from fretes.models import Entrega

DIAS_PADRAO = 30
LIMITE_ENTREGAS = 500  # teto de linhas na tabela de entregas, para o relatório responder rápido (RNF01)
ZERO = Decimal("0")

# Divergência: valor cobrado informado e diferente do sugerido (RF12)
DIVERGENTE = Q(valor_cobrado__isnull=False) & ~Q(valor_cobrado=F("valor_sugerido"))


def periodo_padrao():
    hoje = timezone.localdate()
    return hoje - timedelta(days=DIAS_PADRAO), hoje


def _dec(valor):
    return valor if valor is not None else ZERO


# ----------------------------------------------------------- visão geral
def resumo_geral():
    inicio, fim = periodo_padrao()
    no_periodo = Entrega.objects.filter(data__range=(inicio, fim))
    concluidas = no_periodo.filter(status=Entrega.CONCLUIDA)
    baixos = Material.objects.baixos()

    # Gráfico: só entregas concluídas com valor cobrado, para comparar sugerido e cobrado do mesmo conjunto.
    linhas = list(concluidas.filter(valor_cobrado__isnull=False).values("entregador__nome")
                  .annotate(sugerido=Sum("valor_sugerido"), cobrado=Sum("valor_cobrado")).order_by())
    linhas.sort(key=lambda r: r["entregador__nome"].casefold())
    maior = max([max(r["sugerido"], r["cobrado"]) for r in linhas], default=ZERO)
    for r in linhas:
        r["nome"] = r["entregador__nome"]
        r["curto"] = r["nome"].split()[0]
        r["h_sugerido"] = float(r["sugerido"] / maior * 100) if maior else 0
        r["h_cobrado"] = float(r["cobrado"] / maior * 100) if maior else 0
        r["diferenca"] = r["cobrado"] - r["sugerido"]

    return {
        "inicio": inicio, "fim": fim,
        "n_baixos": baixos.count(),
        "estoque_baixo": baixos.annotate(falta=F("qtd_atual") - F("quantidade_minima")).order_by("falta", "nome")[:8],
        "em_aberto": Entrega.objects.filter(status__in=[Entrega.PENDENTE, Entrega.EM_ANDAMENTO]).count(),
        "abertas": Entrega.objects.select_related("entregador")
        .filter(status__in=[Entrega.PENDENTE, Entrega.EM_ANDAMENTO]).order_by("-data", "-pk")[:5],
        "n_concluidas": concluidas.count(),
        "cobrado_periodo": _dec(concluidas.aggregate(t=Sum("valor_cobrado"))["t"]),
        "n_divergencias": no_periodo.filter(DIVERGENTE).count(),
        "divergentes": no_periodo.filter(DIVERGENTE).select_related("entregador").order_by("-data", "-pk")[:5],
        "grafico": linhas,
    }


# ------------------------------------------------- relatório de movimentações
def relatorio_movimentacoes(material_id, inicio, fim):
    qs = Movimentacao.objects.all()
    if material_id:
        qs = qs.filter(material_id=material_id)
    if inicio:
        qs = qs.filter(data__gte=inicio)
    if fim:
        qs = qs.filter(data__lte=fim)
    saida = lambda motivo: Sum("quantidade", filter=Q(tipo=Movimentacao.SAIDA, motivo=motivo))
    dados = qs.order_by().values("material_id").annotate(
        entradas=Sum("quantidade", filter=Q(tipo=Movimentacao.ENTRADA)), uso_producao=saida("uso_producao"),
        perda_dano=saida("perda_dano"), ajuste_inventario=saida("ajuste_inventario"), total=Count("pk"))
    materiais = Material.objects.in_bulk([d["material_id"] for d in dados])
    linhas = []
    for d in dados:
        m = materiais[d["material_id"]]
        linhas.append({"nome": m.nome, "unidade": m.unidade_medida, "qtd_atual": m.qtd_atual, "baixo": m.esta_baixo,
                       "entradas": d["entradas"] or 0, "uso_producao": d["uso_producao"] or 0,
                       "perda_dano": d["perda_dano"] or 0, "ajuste_inventario": d["ajuste_inventario"] or 0,
                       "total": d["total"]})
    linhas.sort(key=lambda r: r["nome"].casefold())
    return {"linhas": linhas, "total_mov": sum(r["total"] for r in linhas)}


# --------------------------------------------------------- relatório de fretes
def relatorio_fretes(entregador_id, status, inicio, fim, so_divergencias):
    qs = Entrega.objects.all()
    if entregador_id:
        qs = qs.filter(entregador_id=entregador_id)
    if status:
        qs = qs.filter(status=status)
    if inicio:
        qs = qs.filter(data__gte=inicio)
    if fim:
        qs = qs.filter(data__lte=fim)
    if so_divergencias:
        qs = qs.filter(DIVERGENTE)

    com_cobrado = Q(valor_cobrado__isnull=False)
    por_entregador = list(qs.order_by().values("entregador__nome").annotate(
        entregas=Count("pk"), km=Sum("distancia"), sugerido=Sum("valor_sugerido"), cobrado=Sum("valor_cobrado"),
        sugerido_com_cobrado=Sum("valor_sugerido", filter=com_cobrado)))
    resumo = []
    total = {"entregas": 0, "km": ZERO, "sugerido": ZERO, "cobrado": ZERO, "diferenca": ZERO}
    for r in por_entregador:
        linha = {"nome": r["entregador__nome"], "entregas": r["entregas"], "km": _dec(r["km"]),
                 "sugerido": _dec(r["sugerido"]), "cobrado": _dec(r["cobrado"]),
                 # a diferença só conta entregas com valor cobrado informado
                 "diferenca": _dec(r["cobrado"]) - _dec(r["sugerido_com_cobrado"])}
        linha["diferenca_abs"] = abs(linha["diferenca"])
        for chave in total:
            total[chave] += linha[chave]
        resumo.append(linha)
    resumo.sort(key=lambda r: r["nome"].casefold())
    total["diferenca_abs"] = abs(total["diferenca"])

    ordenadas = qs.select_related("entregador").order_by("-data", "-pk")
    return {"resumo": resumo, "total": total, "entregas": list(ordenadas[:LIMITE_ENTREGAS]),
            "limite": LIMITE_ENTREGAS, "passou_do_limite": total["entregas"] > LIMITE_ENTREGAS,
            "n_divergentes": qs.filter(DIVERGENTE).count()}
