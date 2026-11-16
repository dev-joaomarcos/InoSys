from datetime import timedelta

from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import PerfilUsuario, Usuario

SENHA = "Senha-forte-123"

ARMAZENAMENTO_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)

class FluxoContasTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser("admin", SENHA, nome="Ana Souza")
        self.estoque = Usuario.objects.create_user("paula", SENHA, nome="Paula Ribeiro", perfil=PerfilUsuario.ESTOQUE)
        self.temp = Usuario.objects.create_user("novo", "Temp-123456", nome="Novo", perfil=PerfilUsuario.FRETES,
                                                senha_temporaria=True)

    def test_superuser_nasce_administrador(self):
        self.assertEqual(self.admin.perfil, PerfilUsuario.ADMIN)
        self.assertTrue(self.admin.is_staff)

    def test_login_valido_vai_para_selecao(self):
        r = self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA})
        self.assertRedirects(r, reverse("contas:selecao"), fetch_redirect_response=False)

    def test_login_invalido_mostra_erro(self):
        r = self.client.post(reverse("contas:login"), {"username": "paula", "password": "errada"})
        self.assertContains(r, "Usuário ou senha incorretos")

    def test_usuario_inativo_nao_entra(self):
        self.estoque.ativo = False
        self.estoque.save()
        r = self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA})
        self.assertEqual(r.status_code, 200)

    def test_senha_temporaria_forca_troca(self):
        self.client.force_login(self.temp)
        r = self.client.get(reverse("contas:selecao"))
        self.assertRedirects(r, reverse("contas:trocar_senha"), fetch_redirect_response=False)

    def test_troca_de_senha_libera_o_acesso(self):
        self.client.force_login(self.temp)
        r = self.client.post(reverse("contas:trocar_senha"), {
            "old_password": "Temp-123456", "new_password1": "Outra-senha-987", "new_password2": "Outra-senha-987"})
        self.assertRedirects(r, reverse("contas:selecao"), fetch_redirect_response=False)
        self.temp.refresh_from_db()
        self.assertFalse(self.temp.senha_temporaria)

    def test_selecao_mostra_so_modulos_do_perfil(self):
        self.client.force_login(self.estoque)
        r = self.client.get(reverse("contas:selecao"))
        self.assertContains(r, "Abrir estoque")
        self.assertNotContains(r, "Abrir fretes")
        self.assertNotContains(r, "Abrir administração")

    def test_raiz_sem_login_mostra_a_apresentacao(self):
        r = self.client.get(reverse("contas:selecao"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "contas/apresentacao.html")
        self.assertContains(r, 'href="/login/"')
        self.assertContains(r, "Entrar no sistema")

    def test_raiz_com_login_mostra_a_selecao(self):
        self.client.force_login(self.estoque)
        r = self.client.get(reverse("contas:selecao"))
        self.assertTemplateUsed(r, "contas/selecao.html")
        self.assertTemplateNotUsed(r, "contas/apresentacao.html")

    def test_sobre_abre_com_e_sem_login(self):
        r = self.client.get(reverse("contas:apresentacao"))
        self.assertContains(r, "Entrar no sistema")
        self.client.force_login(self.estoque)
        r = self.client.get(reverse("contas:apresentacao"))
        self.assertTemplateUsed(r, "contas/apresentacao.html")
        self.assertContains(r, "Abrir o sistema")
        self.assertNotContains(r, "Entrar no sistema")

    def test_sobre_nao_dispensa_a_troca_de_senha(self):
        self.client.force_login(self.temp)
        r = self.client.get(reverse("contas:apresentacao"))
        self.assertRedirects(r, reverse("contas:trocar_senha"), fetch_redirect_response=False)

    def test_pagina_protegida_sem_login_continua_indo_para_o_login(self):
        r = self.client.get(reverse("estoque:material_lista"))
        self.assertRedirects(r, "/login/?next=/estoque/materiais/", fetch_redirect_response=False)

    def test_login_tem_link_para_a_apresentacao(self):
        self.assertContains(self.client.get(reverse("contas:login")), 'href="/sobre/"')


@override_settings(STORAGES=ARMAZENAMENTO_SIMPLES)
class SessaoTests(TestCase):
    """A sessão cai ao fechar o navegador e após 60 minutos sem uso; o prazo é conferido no servidor."""

    def setUp(self):
        self.paula = Usuario.objects.create_user("paula", SENHA, nome="Paula Ribeiro", perfil=PerfilUsuario.ESTOQUE)
        self.lista = reverse("estoque:material_lista")

    def _sessao(self):
        return Session.objects.get(pk=self.client.session.session_key)

    def test_login_cria_sessao_que_cai_ao_fechar_o_navegador(self):
        self.client.post(reverse("contas:login"), {"username": "paula", "password": SENHA})
        self.assertEqual(self.client.cookies["sessionid"]["max-age"], "")  # cookie de sessão do navegador
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_validade_no_servidor_e_de_60_minutos(self):
        self.client.force_login(self.paula)
        self.client.get(self.lista)
        restante = (self._sessao().expire_date - timezone.now()).total_seconds()
        self.assertAlmostEqual(restante, 3600, delta=30)

    def test_sessao_vencida_volta_para_o_login(self):
        self.client.force_login(self.paula)
        Session.objects.update(expire_date=timezone.now() - timedelta(minutes=1))
        r = self.client.get(self.lista)
        self.assertRedirects(r, reverse("contas:login") + "?next=" + self.lista, fetch_redirect_response=False)

    def test_cada_requisicao_renova_o_prazo(self):
        self.client.force_login(self.paula)
        Session.objects.update(expire_date=timezone.now() + timedelta(minutes=1))
        self.assertEqual(self.client.get(self.lista).status_code, 200)
        restante = (self._sessao().expire_date - timezone.now()).total_seconds()
        self.assertGreater(restante, 3000)

    def test_htmx_sem_sessao_manda_a_pagina_inteira_para_o_login(self):
        r = self.client.get(reverse("estoque:material_novo"), headers={
            "HX-Request": "true", "HX-Current-URL": "http://testserver/estoque/materiais/?status=inativo"})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r["HX-Redirect"], "/login/?next=/estoque/materiais/%3Fstatus%3Dinativo")
        self.assertEqual(r.content, b"")

    def test_htmx_com_senha_temporaria_manda_para_a_troca(self):
        temp = Usuario.objects.create_user("novo", "Temp-123456", perfil=PerfilUsuario.ESTOQUE, senha_temporaria=True)
        self.client.force_login(temp)
        r = self.client.get(reverse("estoque:material_novo"), headers={"HX-Request": "true"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r["HX-Redirect"], reverse("contas:trocar_senha"))
