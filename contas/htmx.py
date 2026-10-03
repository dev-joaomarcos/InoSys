"""Apoio comum às views que respondem ao htmx."""
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.cache import patch_vary_headers


def eh_htmx(request):
    """Pedido do htmx que quer só o trecho. Ao voltar no histórico do navegador, vai a página inteira."""
    return request.headers.get("HX-Request") == "true" and request.headers.get("HX-History-Restore-Request") != "true"


def pagina_ou_trecho(request, pagina, trecho, contexto):
    resposta = render(request, trecho if eh_htmx(request) else pagina, contexto)
    patch_vary_headers(resposta, ["HX-Request"])
    return resposta


def gatilho(resposta, evento, mensagem=None):
    """Acrescenta o HX-Trigger à resposta. Com mensagem, o navegador mostra o aviso flutuante."""
    resposta["HX-Trigger"] = json.dumps({evento: {"mensagem": mensagem} if mensagem else {}})  # ASCII puro
    return resposta


def salvo(evento, mensagem):
    """204 + HX-Trigger: o modal fecha, as listas recarregam e aparece o aviso."""
    return gatilho(HttpResponse(status=204), evento, mensagem)
