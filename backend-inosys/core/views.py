from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Sum
from django.views.generic import TemplateView

from estoque.models import Movimentacao, Produto
from fretes.models import Frete


class Geral(LoginRequiredMixin, TemplateView):
    template_name = "core/geral.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        fretes = Frete.objects.all()
        total = fretes.count()
        atrasados = fretes.filter(status="Atrasado").count()
        por_modal = list(fretes.values("modal").annotate(total=Sum("valor")).order_by("-total"))
        maior = por_modal[0]["total"] if por_modal else 0
        for m in por_modal:
            m["pct"] = float(m["total"] / maior * 100) if maior else 0
        alertas = Produto.objects.filter(quantidade__lte=F("estoque_minimo"))
        ctx.update(
            n_alertas=alertas.count(), alertas=alertas.order_by("quantidade")[:8],
            em_transito=fretes.filter(status="Em trânsito").count(), atrasados=atrasados,
            no_prazo=round(100 * (total - atrasados) / total) if total else None,
            valor_total=fretes.aggregate(t=Sum("valor"))["t"] or 0, por_modal=por_modal,
            ultimas=Movimentacao.objects.select_related("produto")[:6])
        return ctx


class Busca(LoginRequiredMixin, TemplateView):
    template_name = "core/busca.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        ctx["q"] = q
        if q:
            ctx["produtos"] = Produto.objects.filter(Q(nome__icontains=q) | Q(sku__icontains=q))
            ctx["fretes"] = Frete.objects.select_related("entregador").filter(
                Q(codigo__icontains=q) | Q(cliente__icontains=q) | Q(origem__icontains=q)
                | Q(destino__icontains=q) | Q(entregador__nome__icontains=q))
        return ctx
