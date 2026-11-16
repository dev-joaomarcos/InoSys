"""Cria o Administrador inicial a partir de variáveis de ambiente.

Pode rodar em todo deploy: se o usuário já existe ou as variáveis não foram definidas, não faz nada.
A senha informada é temporária: o sistema obriga a troca no primeiro acesso.
"""
import os

from django.core.management.base import BaseCommand

from contas.models import Usuario


class Command(BaseCommand):
    help = "Cria o Administrador inicial (ADMIN_USUARIO / ADMIN_SENHA), se ainda não existir."

    def handle(self, *args, **opcoes):
        username = os.environ.get("ADMIN_USUARIO", "").strip()
        senha = os.environ.get("ADMIN_SENHA", "")
        if not username or not senha:
            self.stdout.write("criar_admin: ADMIN_USUARIO ou ADMIN_SENHA não definidos; nada a fazer.")
            return
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(f"criar_admin: o usuário '{username}' já existe; nada a fazer.")
            return
        Usuario.objects.create_superuser(
            username, senha, nome=os.environ.get("ADMIN_NOME", "Administrador").strip(), senha_temporaria=True)
        self.stdout.write(self.style.SUCCESS(
            f"criar_admin: administrador '{username}' criado. A senha deve ser trocada no primeiro acesso."))
