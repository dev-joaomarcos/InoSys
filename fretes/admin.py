from django.contrib import admin

from .models import Entrega, Entregador


@admin.register(Entregador)
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ("nome", "contato", "valor_por_km", "status")
    list_filter = ("status",)
    search_fields = ("nome", "contato")


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ("data", "destino", "entregador", "distancia", "valor_sugerido", "valor_cobrado", "status")
    list_filter = ("status",)
    readonly_fields = ("valor_sugerido",)  # calculado no servidor
