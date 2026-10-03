"""
Rotas da PRÉVIA do front-end (ver previa_settings.py).

/              -> redireciona para a tela de login
/mockup/...    -> entrega os arquivos de frontend/ (html, css, js, png, svg)

O sidebar.js liga a simulação quando a página está em /mockup/,
do mesmo jeito que faz ao abrir o .html com duplo clique.
"""
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from frontend.previa_settings import PASTA_FRONT

urlpatterns = [
    path('', RedirectView.as_view(url='/mockup/login.html', permanent=False)),
    path('mockup/', RedirectView.as_view(url='/mockup/login.html', permanent=False)),
    # Só tipos de arquivo de tela: os .py e .md desta pasta não são servidos.
    re_path(r'^mockup/(?P<path>[\w./-]+\.(?:html|css|js|png|svg|ico))$', serve, {'document_root': PASTA_FRONT}),
]
