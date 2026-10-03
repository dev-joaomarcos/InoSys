from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from contas.models import PerfilUsuario, Usuario
from estoque.models import Material, Movimentacao
from fretes.models import Entrega, Entregador

SENHA = "Senha-forte-123"
ARMAZENAMENTO_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
HTMX = {"HTTP_HX_REQUEST": "true"}
HOJE = timezone.localdate()


def dias(n):
    return HOJE - timedelta(days=n)


@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)
class RelatoriosBase(TestCase):
    def setUp(self):
        self.gestor = Usuario.objects.create_user("gil", SENHA, nome="Gil Gestor", perfil=PerfilUsuario.GESTOR)
        self.client.force_login(self.gestor)
        self.carlos = Entregador.objects.create(nome="Carlos Menezes", valor_por_km=Decimal("3.00"))
        self.roberto = Entregador.objects.create(nome="Roberto Alves", valor_por_km=Decimal("4.00"))

    def entrega(self, entregador, data, sugerido, cobrado, status="concluida", destino="Obra", km="10"):
        return Entrega.objects.create(entregador=entregador, usuario=self.gestor, destino=destino, data=data,
                                      distancia=Decimal(km), valor_sugerido=Decimal(sugerido),
                                      valor_cobrado=None if cobrado is None else Decimal(cobrado), status=status)

    def movimento(self, material, tipo, qtd, data, motivo=""):
        return Movimentacao.objects.create(material=material, usuario=self.gestor, tipo=tipo, quantidade=qtd,
                                           data=data, motivo=motivo)


class AcessoTests(RelatoriosBase):
    def test_so_gestor_e_administrador_acessam(self):
        urls = [reverse(f"relatorios:{n}") for n in ("visao_geral", "relatorios", "relatorio_movimentacoes", "relatorio_fretes")]
        for perfil in (PerfilUsuario.ESTOQUE, PerfilUsuario.FRETES):
            self.client.force_login(Usuario.objects.create_user(f"u-{perfil}", SENHA, perfil=perfil))
            for url in urls:
                self.assertEqual(self.client.get(url).status_code, 403, url)
        for perfil in (PerfilUsuario.GESTOR, PerfilUsuario.ADMIN):
            self.client.force_login(Usuario.objects.create_user(f"ok-{perfil}", SENHA, perfil=perfil))
            for url in urls:
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_anonimo_vai_para_o_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("relatorios:visao_geral")).status_code, 302)


class VisaoGeralTests(RelatoriosBase):
    def test_indicadores(self):
        Material.objects.create(nome="Massa", unidade_medida="un", quantidade_minima=15, qtd_atual=9)
        Material.objects.create(nome="Perfil", unidade_medida="un", quantidade_minima=5, qtd_atual=50)
        self.entrega(self.carlos, dias(2), "30.00", "30.00")
        self.entrega(self.roberto, dias(3), "40.00", "45.00")
        self.entrega(self.roberto, dias(1), "20.00", None, status="pendente")
        self.entrega(self.carlos, dias(0), "10.00", None, status="em_andamento")
        r = self.client.get(reverse("relatorios:visao_geral"))
        self.assertEqual(r.context["n_baixos"], 1)
        self.assertEqual(r.context["em_aberto"], 2)
        self.assertEqual(r.context["n_concluidas"], 2)
        self.assertEqual(r.context["cobrado_periodo"], Decimal("75.00"))
        self.assertEqual(r.context["n_divergencias"], 1)
        self.assertContains(r, "R$ 75,00")

    def test_so_conta_os_ultimos_30_dias(self):
        self.entrega(self.carlos, dias(31), "30.00", "35.00")
        self.entrega(self.carlos, dias(30), "30.00", "36.00")
        r = self.client.get(reverse("relatorios:visao_geral"))
        self.assertEqual(r.context["n_concluidas"], 1)
        self.assertEqual(r.context["cobrado_periodo"], Decimal("36.00"))
        self.assertEqual(r.context["n_divergencias"], 1)

    def test_grafico_compara_sugerido_e_cobrado_por_entregador(self):
        self.entrega(self.carlos, dias(2), "100.00", "100.00")
        self.entrega(self.roberto, dias(2), "50.00", "60.00")
        self.entrega(self.roberto, dias(2), "80.00", None)  # sem cobrado: fora do gráfico
        r = self.client.get(reverse("relatorios:visao_geral"))
        carlos, roberto = r.context["grafico"]
        self.assertEqual((carlos["sugerido"], carlos["cobrado"], carlos["h_sugerido"]), (100, 100, 100.0))
        self.assertEqual((roberto["sugerido"], roberto["cobrado"]), (50, 60))
        self.assertEqual(roberto["h_cobrado"], 60.0)
        self.assertEqual(r.context["notas_grafico"], [{"nome": "Roberto Alves", "valor": "R$ 10,00", "mais": True}])
        self.assertContains(r, "Roberto Alves cobrou R$ 10,00 a mais")

    def test_telas_vazias_nao_quebram(self):
        r = self.client.get(reverse("relatorios:visao_geral"))
        self.assertContains(r, "Nenhum material abaixo do mínimo.")
        self.assertContains(r, "Nenhuma entrega concluída com valor cobrado")


class RelatorioMovimentacoesTests(RelatoriosBase):
    def setUp(self):
        super().setUp()
        self.massa = Material.objects.create(nome="Massa", unidade_medida="un", quantidade_minima=15, qtd_atual=9)
        self.la = Material.objects.create(nome="Lã de vidro", unidade_medida="m²", quantidade_minima=5, qtd_atual=100)
        self.movimento(self.massa, "entrada", 40, dias(5))
        self.movimento(self.massa, "saida", 10, dias(4), "uso_producao")
        self.movimento(self.massa, "saida", 3, dias(3), "perda_dano")
        self.movimento(self.massa, "saida", 2, dias(2), "ajuste_inventario")
        self.movimento(self.la, "entrada", 7, dias(40))  # fora do período padrão

    def get(self, **params):
        return self.client.get(reverse("relatorios:relatorio_movimentacoes"), params, **HTMX)

    def test_soma_entradas_e_saidas_por_motivo(self):
        linha = self.get().context["mov"]["linhas"][0]
        self.assertEqual((linha["nome"], linha["entradas"], linha["uso_producao"], linha["perda_dano"],
                          linha["ajuste_inventario"], linha["qtd_atual"]), ("Massa", 40, 10, 3, 2, 9))
        self.assertTrue(linha["baixo"])

    def test_so_aparecem_materiais_com_movimentacao_no_periodo(self):
        r = self.get()
        self.assertEqual([x["nome"] for x in r.context["mov"]["linhas"]], ["Massa"])
        self.assertEqual(r.context["mov"]["total_mov"], 4)

    def test_periodo_vazio_nao_limita(self):
        r = self.get(data_inicio="", data_fim="")
        self.assertEqual([x["nome"] for x in r.context["mov"]["linhas"]], ["Lã de vidro", "Massa"])

    def test_filtro_de_material(self):
        r = self.get(material=self.la.pk, data_inicio="", data_fim="")
        self.assertEqual([x["nome"] for x in r.context["mov"]["linhas"]], ["Lã de vidro"])

    def test_trecho_htmx_e_pagina_inteira_no_mesmo_endereco(self):
        trecho = self.get()
        self.assertContains(trecho, 'id="card-rel-movimentacoes"')
        self.assertNotContains(trecho, "<html")
        inteira = self.client.get(reverse("relatorios:relatorio_movimentacoes"))
        self.assertContains(inteira, "<html")
        self.assertContains(inteira, 'id="card-rel-fretes"')  # a página traz os dois relatórios

    def test_data_invalida_nao_quebra(self):
        self.assertEqual(self.get(data_inicio="2026-13-45").status_code, 200)


class RelatorioFretesTests(RelatoriosBase):
    def setUp(self):
        super().setUp()
        self.entrega(self.carlos, dias(5), "30.00", "30.00", km="10")
        self.entrega(self.roberto, dias(4), "40.00", "45.00", km="10", destino="Marechal")
        self.entrega(self.roberto, dias(3), "53.50", "60.00", km="13.4", destino="Mauá")
        self.entrega(self.roberto, dias(2), "20.00", None, status="pendente", km="5", destino="Sem valor")
        self.entrega(self.carlos, dias(60), "99.00", "99.00", destino="Antiga")

    def get(self, **params):
        return self.client.get(reverse("relatorios:relatorio_fretes"), params, **HTMX)

    def test_resumo_por_entregador_e_totais(self):
        r = self.get().context["fre"]
        carlos, roberto = r["resumo"]
        self.assertEqual((carlos["nome"], carlos["entregas"], carlos["sugerido"], carlos["cobrado"], carlos["diferenca"]),
                         ("Carlos Menezes", 1, Decimal("30.00"), Decimal("30.00"), Decimal("0")))
        self.assertEqual((roberto["entregas"], roberto["km"], roberto["sugerido"], roberto["cobrado"]),
                         (3, Decimal("28.4"), Decimal("113.50"), Decimal("105.00")))
        self.assertEqual(r["total"]["entregas"], 4)

    def test_entrega_sem_cobrado_fica_fora_da_diferenca(self):
        roberto = self.get().context["fre"]["resumo"][1]
        # diferença = (45 − 40) + (60 − 53,50); os 20,00 sem cobrado não entram
        self.assertEqual(roberto["diferenca"], Decimal("11.50"))

    def test_so_divergencias(self):
        r = self.get(so_divergencias="1").context["fre"]
        self.assertEqual({e.destino for e in r["entregas"]}, {"Marechal", "Mauá"})
        self.assertEqual(r["n_divergentes"], 2)

    def test_filtros_de_entregador_e_status(self):
        r = self.get(entregador=self.roberto.pk, status="pendente").context["fre"]
        self.assertEqual([e.destino for e in r["entregas"]], ["Sem valor"])

    def test_periodo_padrao_exclui_entregas_antigas_e_vazio_inclui(self):
        self.assertNotIn("Antiga", {e.destino for e in self.get().context["fre"]["entregas"]})
        self.assertIn("Antiga", {e.destino for e in self.get(data_inicio="", data_fim="").context["fre"]["entregas"]})

    def test_pagina_mostra_valores_em_reais(self):
        r = self.get()
        self.assertContains(r, "+R$ 11,50")
        self.assertContains(r, "R$ 113,50")

    def test_endereco_de_fretes_abre_a_aba_certa(self):
        r = self.client.get(reverse("relatorios:relatorio_fretes"))
        self.assertEqual(r.context["aba"], "fretes")
        self.assertContains(r, 'class="tab-pane fade show active" id="painel-fretes"')

    def test_data_invalida_nao_quebra(self):
        self.assertEqual(self.get(data_fim="abc").status_code, 200)
