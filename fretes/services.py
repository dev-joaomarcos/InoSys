from decimal import ROUND_HALF_UP, Decimal


def calcular_sugerido(distancia, valor_por_km):
    """RF08: distância (km) × valor por km, arredondado para centavos (meio para cima)."""
    return (Decimal(distancia) * Decimal(valor_por_km)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
