from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models


class PerfilUsuario(models.TextChoices):
    ESTOQUE = "estoque", "Operacional de Estoque"
    FRETES = "fretes", "Operacional de Fretes"
    GESTOR = "gestor", "Gestor"
    ADMIN = "admin", "Administrador"


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _criar(self, username, password, **extra):
        if not username:
            raise ValueError("O usuário é obrigatório.")
        usuario = self.model(username=username, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, username, password=None, **extra):
        extra.setdefault("perfil", PerfilUsuario.ESTOQUE)
        return self._criar(username, password, **extra)

    def create_superuser(self, username, password=None, **extra):
        extra["perfil"] = PerfilUsuario.ADMIN
        extra["is_superuser"] = True
        return self._criar(username, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """tb_usuarios. A senha fica em `password` (hash padrão do Django, RNF04)."""
    nome = models.CharField(max_length=150, blank=True)
    username = models.CharField("usuário", max_length=150, unique=True)
    perfil = models.CharField(max_length=10, choices=PerfilUsuario.choices, default=PerfilUsuario.ESTOQUE)
    ativo = models.BooleanField(default=True, help_text="Exclusão lógica: inativo não entra no sistema.")
    senha_temporaria = models.BooleanField(default=False, help_text="Obriga a troca de senha no próximo acesso.")
    anonimizado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["nome", "username"]

    def __str__(self):
        return self.nome_exibicao

    # O Django consulta estes dois nomes; aqui eles vêm das regras do projeto.
    @property
    def is_active(self):
        return self.ativo

    @property
    def is_staff(self):
        return self.is_superuser or self.perfil == PerfilUsuario.ADMIN

    @property
    def nome_exibicao(self):
        return self.nome or self.username

    @property
    def iniciais(self):
        partes = self.nome_exibicao.split()
        return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()

    # Quem enxerga cada módulo (README, "Perfis de usuário").
    @property
    def pode_estoque(self):
        return self.perfil in (PerfilUsuario.ESTOQUE, PerfilUsuario.GESTOR, PerfilUsuario.ADMIN)

    @property
    def pode_fretes(self):
        return self.perfil in (PerfilUsuario.FRETES, PerfilUsuario.GESTOR, PerfilUsuario.ADMIN)

    @property
    def pode_visao(self):
        return self.perfil in (PerfilUsuario.GESTOR, PerfilUsuario.ADMIN)

    @property
    def pode_admin(self):
        return self.perfil == PerfilUsuario.ADMIN


class LogAcao(models.Model):
    """tb_log_acoes. O nome do usuário é guardado junto (snapshot) para sobreviver a exclusões."""
    CRIACAO, EDICAO, EXCLUSAO = "criacao", "edicao", "exclusao"
    ACOES = [(CRIACAO, "Criação"), (EDICAO, "Edição"), (EXCLUSAO, "Exclusão")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="logs")
    usuario_nome_snapshot = models.CharField(max_length=150)
    acao = models.CharField(max_length=10, choices=ACOES)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_hora", "-pk"]
        verbose_name = "log de ação"
        verbose_name_plural = "log de ações"

    def __str__(self):
        return f"{self.usuario_nome_snapshot} · {self.get_acao_display()} · {self.data_hora:%d/%m/%Y %H:%M}"
