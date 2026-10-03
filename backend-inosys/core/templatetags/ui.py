from django import template
from django.template.defaultfilters import floatformat
from django.utils.html import format_html

register = template.Library()

VERDE = "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200"
AZUL = "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
VERMELHO = "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
AMBAR = "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200"
CORES = {
    "Entregue": VERDE, "Em trânsito": AZUL, "Atrasado": VERMELHO, "Pendente": AMBAR,
    "Ok": VERDE, "Repor": AMBAR, "Zerado": VERMELHO, "Entrada": VERDE, "Saída": VERMELHO,
}


@register.simple_tag
def badge(texto):
    return format_html(
        '<span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-semibold {}">'
        '<span class="size-2 rounded-full bg-current"></span>{}</span>', CORES.get(texto, AMBAR), texto)


@register.filter
def brl(valor):
    return "R$ " + floatformat(valor or 0, "2g")


@register.filter
def num(valor):
    return floatformat(valor or 0, "-2g")
