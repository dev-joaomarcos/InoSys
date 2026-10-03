from django.core.exceptions import ValidationError
from django.db import transaction

from contas.logs import registrar_log
from contas.models import LogAcao

from .models import Material, Movimentacao


@transaction.atomic
def registrar_movimentacao(usuario, material, tipo, quantidade, data, motivo=""):
    """RF03/RF04: grava a movimentação e atualiza qtd_atual na mesma transação.
    Levanta ValidationError se o material estiver desativado ou o saldo não bastar."""
    material = Material.objects.select_for_update().get(pk=material.pk)  # trava a linha contra saídas simultâneas
    if not material.esta_ativo:
        raise ValidationError("Este material está desativado.")
    if tipo == Movimentacao.SAIDA and quantidade > material.qtd_atual:
        raise ValidationError(f"Saldo insuficiente: há {material.qtd_atual} {material.unidade_medida} em estoque.")
    material.qtd_atual += quantidade if tipo == Movimentacao.ENTRADA else -quantidade
    material.save(update_fields=["qtd_atual"])
    mov = Movimentacao.objects.create(material=material, usuario=usuario, tipo=tipo, quantidade=quantidade,
                                      data=data, motivo=motivo if tipo == Movimentacao.SAIDA else "")
    registrar_log(usuario, LogAcao.CRIACAO)
    return mov
