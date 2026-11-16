"""Regras da administração de usuários: senha temporária e anonimização (RF13, RF15)."""
import secrets

from django.db import transaction

# sem 0/O, 1/l/I: a senha é ditada ou copiada de uma tela
ALFABETO = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
NOME_ANONIMO = "Usuário anonimizado"

# Decisão do grupo (16/11/2026): o nome guardado no log também é dado pessoal,
# então a anonimização troca o nome nos registros de log desse usuário.
ANONIMIZAR_LOG = True


def gerar_senha_temporaria(tamanho=10):
    return "".join(secrets.choice(ALFABETO) for _ in range(tamanho))


@transaction.atomic
def anonimizar_usuario(usuario):
    """RF15: valores fixos genéricos no lugar dos dados pessoais, acesso desativado, sem volta."""
    usuario.nome = NOME_ANONIMO
    usuario.username = f"anonimizado-{usuario.pk}"
    usuario.ativo = False
    usuario.senha_temporaria = False
    usuario.anonimizado = True
    usuario.set_unusable_password()
    usuario.save()
    if ANONIMIZAR_LOG:
        usuario.logs.update(usuario_nome_snapshot=NOME_ANONIMO)
