from django.contrib import admin

from .models import Movimentacao, Produto

admin.site.register(Produto)
admin.site.register(Movimentacao)
