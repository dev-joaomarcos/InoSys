import os
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from .models import PerfilUsuario, Usuario

AMBIENTE = {"ADMIN_USUARIO": "chefe", "ADMIN_SENHA": "Senha-inicial-123", "ADMIN_NOME": "Ana Souza"}


def rodar():
    saida = StringIO()
    call_command("criar_admin", stdout=saida)
    return saida.getvalue()


class CriarAdminTests(TestCase):
    @mock.patch.dict(os.environ, AMBIENTE)
    def test_cria_administrador_com_senha_temporaria(self):
        self.assertIn("criado", rodar())
        admin = Usuario.objects.get(username="chefe")
        self.assertEqual(admin.perfil, PerfilUsuario.ADMIN)
        self.assertEqual(admin.nome, "Ana Souza")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.senha_temporaria)
        self.assertTrue(admin.check_password("Senha-inicial-123"))

    @mock.patch.dict(os.environ, AMBIENTE)
    def test_segunda_execucao_nao_duplica_nem_troca_a_senha(self):
        rodar()
        admin = Usuario.objects.get(username="chefe")
        admin.set_password("Senha-nova-456")
        admin.senha_temporaria = False
        admin.save()
        self.assertIn("já existe", rodar())
        admin.refresh_from_db()
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertTrue(admin.check_password("Senha-nova-456"))
        self.assertFalse(admin.senha_temporaria)

    def test_sem_variaveis_nao_faz_nada_e_nao_falha(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("ADMIN_USUARIO", None)
            os.environ.pop("ADMIN_SENHA", None)
            self.assertIn("nada a fazer", rodar())
        self.assertEqual(Usuario.objects.count(), 0)
