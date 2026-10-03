from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone


class MaterialQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(status=Material.ATIVO)

    def baixos(self):
        """RF05: material ativo com saldo abaixo da quantidade mínima."""
        return self.ativos().filter(qtd_atual__lt=F("quantidade_minima"))


class Material(models.Model):
    """tb_materiais. O saldo fica em qtd_atual e só muda por movimentação."""
    ATIVO, INATIVO = "ativo", "inativo"
    STATUS = [(ATIVO, "Ativo"), (INATIVO, "Desativado")]

    nome = models.CharField(max_length=120)
    descricao = models.TextField("descrição", blank=True)
    unidade_medida = models.CharField("unidade de medida", max_length=10)
    quantidade_minima = models.PositiveIntegerField("quantidade mínima")
    qtd_atual = models.PositiveIntegerField("quantidade atual", default=0)
    status = models.CharField(max_length=10, choices=STATUS, default=ATIVO)

    objects = MaterialQuerySet.as_manager()

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def esta_ativo(self):
        return self.status == self.ATIVO

    @property
    def esta_baixo(self):
        return self.esta_ativo and self.qtd_atual < self.quantidade_minima


class Movimentacao(models.Model):
    """tb_movimentacoes. Registro imutável: o histórico não se edita nem se apaga."""
    ENTRADA, SAIDA = "entrada", "saida"
    TIPOS = [(ENTRADA, "Entrada"), (SAIDA, "Saída")]
    MOTIVOS = [("uso_producao", "Uso em produção"), ("perda_dano", "Perda ou dano"),
               ("ajuste_inventario", "Ajuste de inventário")]

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="movimentacoes")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.PositiveIntegerField()
    data = models.DateField(default=timezone.localdate)
    motivo = models.CharField(max_length=20, choices=MOTIVOS, blank=True, help_text="Só para saída.")

    class Meta:
        ordering = ["-data", "-pk"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} · {self.material}"
