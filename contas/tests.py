from django.test import TestCase, override_settings
from django.urls import reverse

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

    def test_selecao_exige_login(self):
        r = self.client.get(reverse("contas:selecao"))
        self.assertEqual(r.status_code, 302)
