# (url, rótulo, prefixos de url_name que deixam a aba ativa)
ABAS = [
    ("geral", "Visão Geral", ("geral", "busca")),
    ("produto_lista", "Estoque", ("produto_", "entrada", "saida")),
    ("mov_lista", "Movimentações", ("mov_",)),
    ("frete_lista", "Fretes", ("frete_",)),
    ("entregador_lista", "Entregadores", ("entregador_",)),
]


def navegacao(request):
    nome = request.resolver_match.url_name if request.resolver_match else ""
    abas = [(u, t, (nome or "").startswith(p)) for u, t, p in ABAS]
    return {"abas": abas, "pagina": next((t for _, t, ativa in abas if ativa), "InoSys")}
