import re

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import LogAcao, PerfilUsuario, Usuario

SENHA = "Senha-forte-123"
ARMAZENAMENTO_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
HTMX = {"HTTP_HX_REQUEST": "true"}


def senha_da_resposta(resposta):
    return re.search(r"<code[^>]*data-senha[^>]*>([^<]+)</code>", resposta.content.decode()).group(1).strip()


@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)
class GestaoDeUsuariosTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser("ana", SENHA, nome="Ana Souza")
        self.client.force_login(self.admin)
        self.paula = Usuario.objects.create_user("paula", SENHA, nome="Paula Ribeiro", perfil=PerfilUsuario.ESTOQUE)

    def criar(self, **dados):
        base = {"nome": "Lucas Ferreira", "username": "lucas.ferreira", "perfil": "fretes"}
        base.update(dados)
        return self.client.post(reverse("contas:usuario_novo"), base, **HTMX)

    # ---- acesso
    def test_so_administrador_acessa(self):
        for perfil in (PerfilUsuario.ESTOQUE, PerfilUsuario.FRETES, PerfilUsuario.GESTOR):
            self.client.force_login(Usuario.objects.create_user(f"u-{perfil}", SENHA, perfil=perfil))
            self.assertEqual(self.client.get(reverse("contas:usuario_lista")).status_code, 403)
            self.assertEqual(self.client.get(reverse("contas:log_lista")).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("contas:usuario_lista")).status_code, 200)

    def test_pagina_inteira_e_trecho_htmx(self):
        self.assertContains(self.client.get(reverse("contas:usuario_lista")), "<html")
        trecho = self.client.get(reverse("contas:usuario_lista"), **HTMX)
        self.assertContains(trecho, 'id="card-usuarios"')
        self.assertNotContains(trecho, "<html")

    # ---- cadastro e senha temporária
    def test_cadastro_mostra_a_senha_uma_vez_e_exige_troca(self):
        r = self.criar()
        self.assertEqual(r.status_code, 200)
        self.assertIn("usuariosAtualizados", r["HX-Trigger"])
        self.assertIn("no-store", r["Cache-Control"])
        senha = senha_da_resposta(r)
        lucas = Usuario.objects.get(username="lucas.ferreira")
        self.assertTrue(lucas.senha_temporaria)
        self.assertNotIn(senha, lucas.password)  # só o hash fica no banco
        self.client.logout()
        entrada = self.client.post(reverse("contas:login"), {"username": "lucas.ferreira", "password": senha})
        self.assertEqual(entrada.status_code, 302)
        self.assertRedirects(self.client.get(reverse("contas:selecao")), reverse("contas:trocar_senha"),
                             fetch_redirect_response=False)

    def test_usuario_repetido_e_recusado(self):
        r = self.criar(username="paula")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Já existe um usuário com esse nome de acesso.")
        self.assertEqual(Usuario.objects.filter(username="paula").count(), 1)

    def test_usuario_com_espaco_e_recusado(self):
        self.assertContains(self.criar(username="com espaco"), "Informe um usuário válido, sem espaços.")

    def test_perfil_e_nome_sao_obrigatorios(self):
        r = self.criar(nome="", perfil="")
        self.assertContains(r, "Informe o nome.")
        self.assertContains(r, "Escolha o perfil.")

    def test_formulario_novo_comeca_em_selecione(self):
        r = self.client.get(reverse("contas:usuario_novo"), **HTMX)
        self.assertNotContains(r, "selected")

    def test_cadastro_entra_no_log(self):
        self.criar()
        self.assertEqual(LogAcao.objects.filter(usuario=self.admin, acao="criacao").count(), 1)

    # ---- edição
    def test_editar_nome_e_perfil(self):
        r = self.client.post(reverse("contas:usuario_editar", args=[self.paula.pk]),
                             {"nome": "Paula R.", "username": "paula", "perfil": "gestor"}, **HTMX)
        self.assertEqual(r.status_code, 204)
        self.paula.refresh_from_db()
        self.assertEqual((self.paula.nome, self.paula.perfil), ("Paula R.", "gestor"))

    def test_administrador_nao_tira_o_proprio_perfil(self):
        r = self.client.post(reverse("contas:usuario_editar", args=[self.admin.pk]),
                             {"nome": "Ana", "username": "ana", "perfil": "estoque"}, **HTMX)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Você não pode tirar o seu próprio perfil de administrador.")
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.perfil, "admin")

    # ---- nova senha
    def test_nova_senha_derruba_a_antiga(self):
        r = self.client.post(reverse("contas:usuario_nova_senha", args=[self.paula.pk]), **HTMX)
        self.assertEqual(r.status_code, 200)
        nova = senha_da_resposta(r)
        self.paula.refresh_from_db()
        self.assertTrue(self.paula.senha_temporaria)
        self.client.logout()
        self.assertEqual(self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA}).status_code, 200)
        self.assertEqual(self.client.post(reverse("contas:login"), {"username": "paula", "password": nova}).status_code, 302)

    # ---- desativar e reativar
    def test_desativar_bloqueia_o_login_e_reativar_libera(self):
        self.assertEqual(self.client.post(reverse("contas:usuario_desativar", args=[self.paula.pk]), **HTMX).status_code, 204)
        self.client.logout()
        self.assertEqual(self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA}).status_code, 200)
        self.client.force_login(self.admin)
        self.client.post(reverse("contas:usuario_reativar", args=[self.paula.pk]), **HTMX)
        self.client.logout()
        self.assertEqual(self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA}).status_code, 302)

    def test_nao_desativa_o_proprio_acesso(self):
        r = self.client.post(reverse("contas:usuario_desativar", args=[self.admin.pk]), **HTMX)
        self.assertContains(r, "Você não pode desativar o seu próprio acesso.")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.ativo)

    def test_lista_mostra_so_ativos_por_padrao(self):
        self.client.post(reverse("contas:usuario_desativar", args=[self.paula.pk]), **HTMX)
        self.assertNotContains(self.client.get(reverse("contas:usuario_lista"), **HTMX), "Paula Ribeiro")
        self.assertContains(self.client.get(reverse("contas:usuario_lista"), {"status": ""}, **HTMX), "Paula Ribeiro")

    # ---- anonimização
    def test_anonimizar_exige_confirmacao(self):
        r = self.client.post(reverse("contas:usuario_anonimizar", args=[self.paula.pk]), **HTMX)
        self.assertContains(r, "Marque a confirmação para anonimizar.")
        self.paula.refresh_from_db()
        self.assertFalse(self.paula.anonimizado)

    def test_anonimizar_troca_dados_por_valores_genericos(self):
        from .logs import registrar_log
        registrar_log(self.paula, LogAcao.CRIACAO)
        r = self.client.post(reverse("contas:usuario_anonimizar", args=[self.paula.pk]), {"confirmacao": "1"}, **HTMX)
        self.assertEqual(r.status_code, 204)
        self.paula.refresh_from_db()
        self.assertEqual((self.paula.nome, self.paula.username), ("Usuário anonimizado", f"anonimizado-{self.paula.pk}"))
        self.assertTrue(self.paula.anonimizado)
        self.assertFalse(self.paula.ativo)
        self.assertFalse(self.paula.has_usable_password())
        self.assertFalse(LogAcao.objects.filter(usuario_nome_snapshot="Paula Ribeiro").exists())

    def test_anonimizado_nao_volta(self):
        self.client.post(reverse("contas:usuario_anonimizar", args=[self.paula.pk]), {"confirmacao": "1"}, **HTMX)
        for nome in ("usuario_editar", "usuario_nova_senha", "usuario_reativar", "usuario_anonimizar"):
            self.assertEqual(self.client.get(reverse(f"contas:{nome}", args=[self.paula.pk]), **HTMX).status_code, 404)

    def test_nao_anonimiza_a_si_mesmo(self):
        r = self.client.post(reverse("contas:usuario_anonimizar", args=[self.admin.pk]), {"confirmacao": "1"}, **HTMX)
        self.assertContains(r, "Você não pode anonimizar o seu próprio usuário.")
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.anonimizado)

    # ---- log
    def test_log_lista_e_filtra(self):
        self.criar()
        self.client.post(reverse("contas:usuario_editar", args=[self.paula.pk]),
                         {"nome": "Paula R.", "username": "paula", "perfil": "estoque"}, **HTMX)
        todos = self.client.get(reverse("contas:log_lista"))
        self.assertContains(todos, "Ana Souza")
        so_edicao = self.client.get(reverse("contas:log_lista"), {"acao": "edicao"}, **HTMX)
        self.assertContains(so_edicao, "Edição")
        self.assertNotContains(so_edicao, "Criação</span>")

    def test_log_pagina_de_20_em_20(self):
        LogAcao.objects.bulk_create([LogAcao(usuario=self.admin, usuario_nome_snapshot="Ana Souza", acao="edicao")
                                     for _ in range(25)])
        self.assertContains(self.client.get(reverse("contas:log_lista")), "Página 1 de 2")

    def test_data_invalida_no_filtro_do_log_nao_quebra(self):
        self.assertEqual(self.client.get(reverse("contas:log_lista"), {"data_inicio": "2026-13-45"}).status_code, 200)
