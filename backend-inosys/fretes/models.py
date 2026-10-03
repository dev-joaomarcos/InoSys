from django.core.validators import MinValueValidator
from django.db import models

MODAIS = [(m, m) for m in ("Rodoviário", "Marítimo", "Aéreo", "Ferroviário")]
STATUS = [(s, s) for s in ("Pendente", "Em trânsito", "Entregue", "Atrasado")]


class Entregador(models.Model):
    nome = models.CharField(max_length=120, help_text="Pessoa ou transportadora")
    telefone = models.CharField(max_length=20, blank=True)
    veiculo = models.CharField("Veículo", max_length=60, blank=True, help_text="Ex.: Moto, Van, Caminhão")

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Frete(models.Model):
    codigo = models.CharField("Rastreio", max_length=12, unique=True, null=True, editable=False)
    cliente = models.CharField(max_length=120, blank=True)
    origem = models.CharField(max_length=80)
    destino = models.CharField(max_length=80)
    entregador = models.ForeignKey(Entregador, on_delete=models.PROTECT, related_name="fretes")
    modal = models.CharField(max_length=20, choices=MODAIS, default="Rodoviário")
    previsao = models.DateField("Previsão de entrega")
    status = models.CharField(max_length=20, choices=STATUS, default="Pendente")
    valor = models.DecimalField("Valor cobrado (R$)", max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    observacao = models.CharField("Observação", max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-previsao", "-pk"]

    def __str__(self):
        return f"{self.codigo} · {self.origem} → {self.destino}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo:  # código gerado a partir do id: FR-00042
            self.codigo = f"FR-{self.pk:05d}"
            super().save(update_fields=["codigo"])
