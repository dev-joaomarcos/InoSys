import os
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Q, Sum
from django.test import TestCase

from contas.models import PerfilUsuario, Usuario
from estoque.models import Material, Movimentacao
from fretes.models import Entrega, Entregador

from . import services

SENHA = "Demo-senha-123"


def rodar(*args):
    saida = StringIO()
    call_command("popular_demo", *args, stdout=saida)
    return saida.getvalue()


class PopularDemoTests(TestCase):
    def test_cria_o_cenario_do_roteiro(self):
        rodar("--senha", SENHA)
        self.assertEqual(Material.objects.count(), 9)
        self.assertEqual(Movimentacao.objects.count(), 25)
        self.assertEqual(Entregador.objects.count(), 4)
        self.assertEqual(Entrega.objects.count(), 20)
        self.assertEqual(Material.objects.filter(status=Material.INATIVO).count(), 1)
        self.assertEqual(Entregador.objects.filter(status=Entregador.INATIVO).count(), 1)
        for username, perfil in (("paula", PerfilUsuario.ESTOQUE), ("fabio", PerfilUsuario.FRETES),
                                 ("gustavo", PerfilUsuario.GESTOR)):
            usuario = Usuario.objects.get(username=username)
            self.assertEqual(usuario.perfil, perfil)
            self.assertTrue(usuario.check_password(SENHA))
            self.assertFalse(usuario.senha_temporaria)

    def test_numeros_que_o_roteiro_cita(self):
        rodar("--senha", SENHA)
        self.assertEqual(sorted(Material.objects.baixos().values_list("nome", "qtd_atual")),
                         [("Massa para junta", 9), ("Perfil guia 48 mm", 8), ("Placa de gesso acartonado 12,5 mm", 14)])
        r = services.resumo_geral()
        self.assertEqual(r["n_baixos"], 3)
        self.assertEqual(r["em_aberto"], 5)
        self.assertEqual(r["n_concluidas"], 15)
        self.assertEqual(r["n_divergencias"], 4)
        self.assertEqual(r["cobrado_periodo"], Decimal("1176.45"))
        self.assertEqual(Entrega.objects.filter(status=Entrega.PENDENTE).count(), 3)
        self.assertEqual(Entrega.objects.filter(status=Entrega.EM_ANDAMENTO).count(), 2)

    def test_saldo_bate_com_as_movimentacoes(self):
        rodar("--senha", SENHA)
        for material in Material.objects.all():
            soma = material.movimentacoes.aggregate(
                e=Sum("quantidade", filter=Q(tipo=Movimentacao.ENTRADA)),
                s=Sum("quantidade", filter=Q(tipo=Movimentacao.SAIDA)))
            self.assertEqual(material.qtd_atual, (soma["e"] or 0) - (soma["s"] or 0), material.nome)

    def test_recusa_banco_com_dados(self):
        rodar("--senha", SENHA)
        with self.assertRaises(CommandError):
            rodar("--senha", SENHA)
        self.assertEqual(Material.objects.count(), 9)

    def test_exige_senha(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("DEMO_SENHA", None)
            with self.assertRaises(CommandError):
                rodar()
        self.assertEqual(Material.objects.count(), 0)

    def test_se_vazio_sai_sem_erro(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("DEMO_SENHA", None)
            self.assertIn("nada a fazer", rodar("--se-vazio"))
        rodar("--senha", SENHA)
        self.assertIn("nada a fazer", rodar("--se-vazio", "--senha", SENHA))
        self.assertEqual(Entrega.objects.count(), 20)

    def test_senha_pela_variavel_de_ambiente(self):
        with mock.patch.dict(os.environ, {"DEMO_SENHA": SENHA}):
            rodar("--se-vazio")
        self.assertTrue(Usuario.objects.get(username="gustavo").check_password(SENHA))
