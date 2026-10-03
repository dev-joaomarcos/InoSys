from django.contrib import admin

from .models import Material, Movimentacao


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("nome", "unidade_medida", "qtd_atual", "quantidade_minima", "status")
    list_filter = ("status",)
    search_fields = ("nome", "descricao")
    readonly_fields = ("qtd_atual",)  # o saldo só muda por movimentação


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("data", "material", "tipo", "quantidade", "motivo", "usuario")
    list_filter = ("tipo", "motivo")

    def has_add_permission(self, request):
        return False  # entradas e saídas passam por registrar_movimentacao

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
