from django.utils.formats import number_format


def moeda(valor):
    """1234.5 -> 'R$ 1.234,50' (pontuação conforme o idioma configurado)."""
    return "R$ " + number_format(valor, decimal_pos=2, force_grouping=True)


def numero(valor, casas=1):
    return number_format(valor, decimal_pos=casas, force_grouping=True)
