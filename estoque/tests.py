import json

from django.test import TestCase, override_settings
from django.urls import reverse

from contas.models import PerfilUsuario, Usuario

from .models import Material, Movimentacao

SENHA = "Senha-forte-123"
# Nos testes não há collectstatic; usa o armazenamento simples.
ARMAZENAMENTO_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
HTMX = {"HTTP_HX_REQUEST": "true"}


@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)
class EstoqueTests(TestCase):
    def setUp(self):
        self.op = Usuario.objects.create_user("paula", SENHA, nome="Paula Ribeiro", perfil=PerfilUsuario.ESTOQUE)
        self.client.force_login(self.op)
        self.m = Material.objects.create(nome="Perfil montante", unidade_medida="un", quantidade_minima=10, qtd_atual=5)

    def mover(self, **dados):
        base = {"tipo": "entrada", "material": self.m.pk, "quantidade": 1, "data": "2026-10-03"}
        base.update(dados)
        return self.client.post(reverse("estoque:movimentacao_nova"), base, **HTMX)

    def test_perfil_de_fretes_nao_acessa_estoque(self):
        self.client.force_login(Usuario.objects.create_user("diego", SENHA, perfil=PerfilUsuario.FRETES))
        self.assertEqual(self.client.get(reverse("estoque:material_lista")).status_code, 403)

    def test_anonimo_vai_para_o_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("estoque:material_lista")).status_code, 302)

    def test_pagina_inteira_e_trecho_htmx(self):
        inteira = self.client.get(reverse("estoque:material_lista"))
        self.assertContains(inteira, "<html")
        self.assertContains(inteira, "Materiais ativos")
        trecho = self.client.get(reverse("estoque:material_lista"), **HTMX)
        self.assertContains(trecho, 'id="card-materiais"')
        self.assertNotContains(trecho, "<html")
        self.assertNotContains(trecho, 'id="resumo-estoque"')

    def test_novo_material_responde_204_com_gatilho(self):
        r = self.client.post(reverse("estoque:material_novo"), {
            "nome": "Lã de vidro", "unidade_medida": "m²", "quantidade_minima": 80, "descricao": ""}, **HTMX)
        self.assertEqual(r.status_code, 204)
        self.assertIn("estoqueAtualizado", json.loads(r["HX-Trigger"]))
        novo = Material.objects.get(nome="Lã de vidro")
        self.assertEqual((novo.qtd_atual, novo.status), (0, "ativo"))

    def test_material_invalido_volta_com_erro(self):
        r = self.client.post(reverse("estoque:material_novo"), {"nome": "", "unidade_medida": "un",
                                                                 "quantidade_minima": 1}, **HTMX)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Informe o nome do material.")

    def test_editar_nao_mexe_no_saldo(self):
        r = self.client.post(reverse("estoque:material_editar", args=[self.m.pk]), {
            "nome": "Perfil montante 70", "unidade_medida": "un", "quantidade_minima": 20, "qtd_atual": 999}, **HTMX)
        self.assertEqual(r.status_code, 204)
        self.m.refresh_from_db()
        self.assertEqual((self.m.nome, self.m.quantidade_minima, self.m.qtd_atual), ("Perfil montante 70", 20, 5))

    def test_entrada_atualiza_saldo_e_historico(self):
        self.assertEqual(self.mover(quantidade=7).status_code, 204)
        self.m.refresh_from_db()
        self.assertEqual(self.m.qtd_atual, 12)
        mov = Movimentacao.objects.get()
        self.assertEqual((mov.tipo, mov.quantidade, mov.usuario, mov.motivo), ("entrada", 7, self.op, ""))

    def test_saida_exige_motivo(self):
        r = self.mover(tipo="saida", quantidade=2)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Escolha o motivo da saída.")
        self.m.refresh_from_db()
        self.assertEqual(self.m.qtd_atual, 5)

    def test_saida_maior_que_o_saldo_e_recusada(self):
        r = self.mover(tipo="saida", quantidade=6, motivo="perda_dano")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Saldo insuficiente: há 5 un em estoque.")
        self.m.refresh_from_db()
        self.assertEqual(self.m.qtd_atual, 5)
        self.assertEqual(Movimentacao.objects.count(), 0)

    def test_saida_valida_baixa_o_saldo(self):
        self.assertEqual(self.mover(tipo="saida", quantidade=3, motivo="uso_producao").status_code, 204)
        self.m.refresh_from_db()
        self.assertEqual(self.m.qtd_atual, 2)
        self.assertEqual(Movimentacao.objects.get().motivo, "uso_producao")

    def test_desativar_tira_do_formulario_e_reativar_devolve(self):
        self.assertEqual(self.client.post(reverse("estoque:material_desativar", args=[self.m.pk]), **HTMX).status_code, 204)
        self.m.refresh_from_db()
        self.assertEqual(self.m.status, "inativo")
        r = self.client.get(reverse("estoque:movimentacao_nova"), **HTMX)
        self.assertNotContains(r, "Perfil montante")
        self.assertEqual(self.mover().status_code, 200)  # material desativado não recebe movimentação
        self.client.post(reverse("estoque:material_reativar", args=[self.m.pk]), **HTMX)
        self.m.refresh_from_db()
        self.assertEqual(self.m.status, "ativo")

    def test_alerta_de_estoque_baixo(self):
        Material.objects.create(nome="Massa", unidade_medida="un", quantidade_minima=1, qtd_atual=50)
        r = self.client.get(reverse("estoque:material_resumo"))
        self.assertContains(r, "abaixo da quantidade mínima")
        self.assertContains(r, "Perfil montante")
        self.assertNotContains(r, "Massa")

    def test_filtro_de_situacao_baixo(self):
        Material.objects.create(nome="Massa", unidade_medida="un", quantidade_minima=1, qtd_atual=50)
        r = self.client.get(reverse("estoque:material_lista"), {"situacao": "baixo"}, **HTMX)
        self.assertContains(r, "Perfil montante")
        self.assertNotContains(r, "Massa")

    def test_paginacao_de_20_itens(self):
        Material.objects.bulk_create([Material(nome=f"Item {i:02d}", unidade_medida="un", quantidade_minima=1,
                                               qtd_atual=5) for i in range(24)])  # 25 com o do setUp
        self.assertContains(self.client.get(reverse("estoque:material_lista")), "Página 1 de 2")
        self.assertContains(self.client.get(reverse("estoque:material_lista"), {"pagina": 2}), "Página 2 de 2")

    def test_historico_filtra_por_tipo(self):
        self.mover(quantidade=2)
        self.mover(tipo="saida", quantidade=1, motivo="perda_dano")
        r = self.client.get(reverse("estoque:movimentacao_lista"), {"tipo": "saida"}, **HTMX)
        self.assertContains(r, "Perda ou dano")
        self.assertNotContains(r, "Entrada</span>")

    def test_data_invalida_no_filtro_nao_quebra(self):
        r = self.client.get(reverse("estoque:movimentacao_lista"), {"data_inicio": "2026-13-45"})
        self.assertEqual(r.status_code, 200)
