from .models import LogAcao


def registrar_log(usuario, acao):
    """RF14: registro manual dentro das views. `acao` = LogAcao.CRIACAO / EDICAO / EXCLUSAO."""
    LogAcao.objects.create(
        usuario=usuario if getattr(usuario, "pk", None) else None,
        usuario_nome_snapshot=getattr(usuario, "nome_exibicao", str(usuario)),
        acao=acao,
    )
