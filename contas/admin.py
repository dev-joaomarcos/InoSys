from django.contrib import admin

from .models import LogAcao, Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "nome", "perfil", "ativo", "senha_temporaria")
    list_filter = ("perfil", "ativo")
    search_fields = ("username", "nome")
    readonly_fields = ("password", "last_login", "data_criacao")

    def has_add_permission(self, request):
        return False  # usuários nascem na tela de Administração (senha temporária) ou no createsuperuser


@admin.register(LogAcao)
class LogAcaoAdmin(admin.ModelAdmin):
    list_display = ("data_hora", "usuario_nome_snapshot", "acao")
    list_filter = ("acao",)
