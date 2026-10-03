from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class EntregadorQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(status=Entregador.ATIVO)


class Entregador(models.Model):
    """tb_entregadores. Desativa em vez de excluir (RNF02)."""
    ATIVO, INATIVO = "ativo", "inativo"
    STATUS = [(ATIVO, "Ativo"), (INATIVO, "Desativado")]

    nome = models.CharField(max_length=120)
    contato = models.CharField(max_length=120, blank=True)
    valor_por_km = models.DecimalField("valor por km (R$)", max_digits=8, decimal_places=2,
                                       validators=[MinValueValidator(Decimal("0.01"))])
    status = models.CharField(max_length=10, choices=STATUS, default=ATIVO)

    objects = EntregadorQuerySet.as_manager()

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def esta_ativo(self):
        return self.status == self.ATIVO


class Entrega(models.Model):
    """tb_entregas. valor_sugerido = distância × valor por km do entregador, calculado no servidor."""
    PENDENTE, EM_ANDAMENTO, CONCLUIDA = "pendente", "em_andamento", "concluida"
    STATUS = [(PENDENTE, "Pendente"), (EM_ANDAMENTO, "Em andamento"), (CONCLUIDA, "Concluída")]

    entregador = models.ForeignKey(Entregador, on_delete=models.PROTECT, related_name="entregas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+",
                                help_text="Quem registrou a entrega.")
    destino = models.CharField(max_length=200)
    data = models.DateField(default=timezone.localdate)
    distancia = models.DecimalField("distância (km)", max_digits=8, decimal_places=1,
                                    validators=[MinValueValidator(Decimal("0.1"))])
    valor_sugerido = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    valor_cobrado = models.DecimalField("valor cobrado (R$)", max_digits=10, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(Decimal("0"))])
    status = models.CharField(max_length=15, choices=STATUS, default=PENDENTE)

    class Meta:
        ordering = ["-data", "-pk"]
        verbose_name_plural = "entregas"

    def __str__(self):
        return f"{self.destino} · {self.data:%d/%m/%Y}"

    @property
    def divergente(self):
        """Cobrado informado e diferente do sugerido (RF12)."""
        return self.valor_cobrado is not None and self.valor_cobrado != self.valor_sugerido

    @property
    def diferenca(self):
        return self.valor_cobrado - self.valor_sugerido if self.divergente else Decimal("0")

    @property
    def diferenca_abs(self):
        return abs(self.diferenca)
