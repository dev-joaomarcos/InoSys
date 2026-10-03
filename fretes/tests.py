import json
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from contas.models import PerfilUsuario, Usuario

from .models import Entrega, Entregador
from .services import calcular_sugerido

SENHA = "Senha-forte-123"
ARMAZENAMENTO_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
HTMX = {"HTTP_HX_REQUEST": "true"}


class CalculoTests(TestCase):
    def test_sugerido_e_distancia_vezes_valor_por_km(self):
        self.assertEqual(calcular_sugerido(Decimal("10.5"), Decimal("3.20")), Decimal("33.60"))

    def test_arredonda_meio_para_cima(self):
        self.assertEqual(calcular_sugerido(Decimal("3.3"), Decimal("1.25")), Decimal("4.13"))  # 4,125


@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)
class FretesTests(TestCase):
    def setUp(self):
        self.op = Usuario.objects.create_user("diego", SENHA, nome="Diego Alves", perfil=PerfilUsuario.FRETES)
        self.client.force_login(self.op)
        self.ent = Entregador.objects.create(nome="Carlos Mendes", contato="(11) 99999-0000", valor_por_km=Decimal("3.20"))

    def nova(self, **dados):
        base = {"entregador": self.ent.pk, "data": "2026-10-03", "destino": "Obra Vila Nova",
                "distancia": "10.5", "valor_cobrado": "", "status": "pendente"}
        base.update(dados)
        return self.client.post(reverse("fretes:entrega_nova"), base, **HTMX)

    # ---- acesso
    def test_perfil_de_estoque_nao_acessa_fretes(self):
        self.client.force_login(Usuario.objects.create_user("paula", SENHA, perfil=PerfilUsuario.ESTOQUE))
        self.assertEqual(self.client.get(reverse("fretes:entrega_lista")).status_code, 403)

    def test_gestor_acessa_fretes(self):
        self.client.force_login(Usuario.objects.create_user("gil", SENHA, perfil=PerfilUsuario.GESTOR))
        self.assertEqual(self.client.get(reverse("fretes:entrega_lista")).status_code, 200)

    def test_pagina_inteira_e_trecho_htmx(self):
        self.assertContains(self.client.get(reverse("fretes:entrega_lista")), "<html")
        trecho = self.client.get(reverse("fretes:entrega_lista"), **HTMX)
        self.assertContains(trecho, 'id="card-entregas"')
        self.assertNotContains(trecho, "<html")

    # ---- entregas
    def test_nova_entrega_calcula_sugerido_no_servidor(self):
        r = self.nova(valor_sugerido="999")  # o valor enviado pelo navegador é ignorado
        self.assertEqual(r.status_code, 204)
        self.assertIn("fretesAtualizados", json.loads(r["HX-Trigger"]))
        e = Entrega.objects.get()
        self.assertEqual((e.valor_sugerido, e.valor_cobrado, e.usuario), (Decimal("33.60"), None, self.op))
        self.assertFalse(e.divergente)

    def test_cobrado_diferente_do_sugerido_e_divergencia(self):
        self.nova(valor_cobrado="35.00")
        e = Entrega.objects.get()
        self.assertTrue(e.divergente)
        self.assertEqual(e.diferenca, Decimal("1.40"))
        self.assertContains(self.client.get(reverse("fretes:entrega_lista")), "+R$ 1,40")

    def test_cobrado_igual_ao_sugerido_nao_diverge(self):
        self.nova(valor_cobrado="33.60")
        self.assertFalse(Entrega.objects.get().divergente)

    def test_entrega_invalida_volta_com_erro(self):
        r = self.nova(destino="", distancia="")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Informe o destino.")
        self.assertContains(r, "Informe a distância em km.")
        self.assertEqual(Entrega.objects.count(), 0)

    def test_editar_status_nao_recalcula_o_sugerido(self):
        self.nova()
        e = Entrega.objects.get()
        self.ent.valor_por_km = Decimal("5.00")  # tarifa mudou depois
        self.ent.save()
        r = self.client.post(reverse("fretes:entrega_editar", args=[e.pk]), {
            "entregador": self.ent.pk, "data": "2026-10-03", "destino": "Obra Vila Nova", "distancia": "10.5",
            "valor_cobrado": "", "status": "concluida"}, **HTMX)
        self.assertEqual(r.status_code, 204)
        e.refresh_from_db()
        self.assertEqual((e.status, e.valor_sugerido), ("concluida", Decimal("33.60")))

    def test_editar_distancia_recalcula_com_a_tarifa_atual(self):
        self.nova()
        e = Entrega.objects.get()
        self.ent.valor_por_km = Decimal("5.00")
        self.ent.save()
        self.client.post(reverse("fretes:entrega_editar", args=[e.pk]), {
            "entregador": self.ent.pk, "data": "2026-10-03", "destino": "Obra Vila Nova", "distancia": "20",
            "valor_cobrado": "", "status": "pendente"}, **HTMX)
        e.refresh_from_db()
        self.assertEqual(e.valor_sugerido, Decimal("100.00"))

    def test_entregador_desativado_sai_do_form_novo_mas_fica_na_edicao(self):
        self.nova()
        e = Entrega.objects.get()
        self.ent.status = "inativo"
        self.ent.save()
        self.assertNotContains(self.client.get(reverse("fretes:entrega_nova"), **HTMX), "Carlos Mendes")
        self.assertContains(self.client.get(reverse("fretes:entrega_editar", args=[e.pk]), **HTMX), "Carlos Mendes")

    def test_endpoint_valor_sugerido(self):
        r = self.client.get(reverse("fretes:valor_sugerido"), {"entregador": self.ent.pk, "distancia": "10.5"}, **HTMX)
        self.assertContains(r, 'data-valor="33.60"')
        vazio = self.client.get(reverse("fretes:valor_sugerido"), {"entregador": "", "distancia": "abc"}, **HTMX)
        self.assertContains(vazio, 'data-valor=""')
        self.assertEqual(self.client.get(reverse("fretes:valor_sugerido"),
                                         {"entregador": self.ent.pk, "distancia": "NaN"}).status_code, 200)

    def test_resumo_conta_status_e_divergencias(self):
        self.nova(valor_cobrado="40.00")
        self.nova(status="concluida")
        r = self.client.get(reverse("fretes:entrega_resumo"))
        self.assertEqual([r.context[k] for k in ("pendentes", "andamento", "concluidas", "divergencias")], [1, 0, 1, 1])

    def test_filtros_da_lista(self):
        outro = Entregador.objects.create(nome="Ana Souza", valor_por_km=Decimal("2.00"))
        self.nova(destino="Obra A")
        self.nova(destino="Obra B", entregador=outro.pk, status="concluida")
        r = self.client.get(reverse("fretes:entrega_lista"), {"entregador": outro.pk}, **HTMX)
        self.assertContains(r, "Obra B")
        self.assertNotContains(r, "Obra A")
        r = self.client.get(reverse("fretes:entrega_lista"), {"status": "pendente"}, **HTMX)
        self.assertContains(r, "Obra A")
        self.assertNotContains(r, "Obra B")

    def test_paginacao_de_20_itens(self):
        Entrega.objects.bulk_create([Entrega(entregador=self.ent, usuario=self.op, destino=f"Obra {i}", distancia=1,
                                             valor_sugerido=3.2) for i in range(25)])
        self.assertContains(self.client.get(reverse("fretes:entrega_lista")), "Página 1 de 2")

    def test_data_invalida_no_filtro_nao_quebra(self):
        self.assertEqual(self.client.get(reverse("fretes:entrega_lista"), {"data_inicio": "2026-13-45"}).status_code, 200)

    # ---- entregadores
    def test_novo_entregador(self):
        r = self.client.post(reverse("fretes:entregador_novo"), {"nome": "Ana Souza", "contato": "", "valor_por_km": "2.50"}, **HTMX)
        self.assertEqual(r.status_code, 204)
        self.assertIn("entregadoresAtualizados", json.loads(r["HX-Trigger"]))
        self.assertEqual(Entregador.objects.get(nome="Ana Souza").valor_por_km, Decimal("2.50"))

    def test_valor_por_km_zero_e_recusado(self):
        r = self.client.post(reverse("fretes:entregador_novo"), {"nome": "Ana", "valor_por_km": "0"}, **HTMX)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Informe um valor maior que zero.")

    def test_desativar_e_reativar_entregador(self):
        self.client.post(reverse("fretes:entregador_desativar", args=[self.ent.pk]), **HTMX)
        self.ent.refresh_from_db()
        self.assertEqual(self.ent.status, "inativo")
        self.assertNotContains(self.client.get(reverse("fretes:entregador_lista"), **HTMX), "Carlos Mendes")
        self.client.post(reverse("fretes:entregador_reativar", args=[self.ent.pk]), **HTMX)
        self.ent.refresh_from_db()
        self.assertEqual(self.ent.status, "ativo")
