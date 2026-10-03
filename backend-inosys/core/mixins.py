from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.utils.cache import patch_vary_headers
from django.views.generic import CreateView, DeleteView, ListView, UpdateView  # noqa: F401


class Lista(LoginRequiredMixin, ListView):
    """Lista com busca (?q=), filtro (?st=) e ordenação (?ordem=&dir=).
    Requisições do htmx (HX-Request) recebem só o fragmento da tabela."""
    template_name = "crud/lista.html"
    partial = None
    titulo_lista = ""
    url_novo = None
    rotulo_novo = "Novo"
    campos_busca = ()
    campo_status = None
    opcoes_status = ()
    ordenaveis = ()

    def filtrar_status(self, qs, st):
        return qs.filter(**{self.campo_status: st}) if self.campo_status else qs

    def get_queryset(self):
        qs = super().get_queryset()
        g = self.request.GET
        q = g.get("q", "").strip()
        if q:
            cond = Q()
            for campo in self.campos_busca:
                cond |= Q(**{campo + "__icontains": q})
            qs = qs.filter(cond)
        if g.get("st"):
            qs = self.filtrar_status(qs, g["st"])
        if g.get("ordem") in self.ordenaveis:
            qs = qs.order_by(("-" if g.get("dir") == "desc" else "") + g["ordem"], "pk")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        g = self.request.GET
        ctx.update(q=g.get("q", ""), st=g.get("st", ""), ordem=g.get("ordem", ""), dir=g.get("dir", "asc"),
                   partial=self.partial, titulo_lista=self.titulo_lista, url_novo=self.url_novo,
                   rotulo_novo=self.rotulo_novo, opcoes_status=self.opcoes_status)
        return ctx

    def get_template_names(self):
        if self.request.headers.get("HX-Request") and self.partial:
            return [self.partial]
        return super().get_template_names()

    def render_to_response(self, context, **kwargs):
        resposta = super().render_to_response(context, **kwargs)
        patch_vary_headers(resposta, ["HX-Request"])
        return resposta


class Form(LoginRequiredMixin):
    """Comportamento comum de criar/editar: template único, título e mensagem de sucesso."""
    template_name = "crud/form.html"
    titulo = ""
    mensagem = "Salvo com sucesso."

    def get_titulo(self):
        return self.titulo

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titulo=self.get_titulo(), voltar=self.success_url)
        return ctx

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, self.mensagem)
        return resposta


class Criar(Form, CreateView):
    pass


class Editar(Form, UpdateView):
    pass


class Excluir(LoginRequiredMixin, DeleteView):
    template_name = "crud/confirm_delete.html"
    aviso = ""
    mensagem = "Excluído com sucesso."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(aviso=self.aviso, voltar=self.success_url)
        return ctx

    def form_valid(self, form):
        try:
            resposta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Não foi possível excluir: há registros vinculados a este item.")
            return redirect(self.success_url)
        messages.success(self.request, self.mensagem)
        return resposta
