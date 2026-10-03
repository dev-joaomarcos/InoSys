from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    sku = models.CharField("Código (SKU)", max_length=40, unique=True)
    unidade = models.CharField(max_length=10, default="un", help_text="Ex.: un, kg, cx")
    quantidade = models.DecimalField("Em estoque", max_digits=12, decimal_places=2, default=0,
                                     validators=[MinValueValidator(0)])
    estoque_minimo = models.DecimalField("Estoque mínimo", max_digits=12, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)],
                                         help_text="Quando o saldo chegar a esse valor, o produto entra no alerta de reposição.")

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def situacao(self):
        if self.quantidade <= 0:
            return "Zerado"
        return "Repor" if self.quantidade <= self.estoque_minimo else "Ok"


class Movimentacao(models.Model):
    ENTRADA, SAIDA = "E", "S"
    TIPOS = [(ENTRADA, "Entrada"), (SAIDA, "Saída")]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="movimentacoes")
    tipo = models.CharField(max_length=1, choices=TIPOS)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    data = models.DateField(default=timezone.localdate)
    observacao = models.CharField("Observação", max_length=200, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-pk"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} · {self.produto}"
