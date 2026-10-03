"""
Configuração de PRÉVIA do front-end (só para testar as telas no navegador).

Uso, na raiz do projeto, com o .venv ativo:
    python manage.py runserver --settings=frontend.previa_settings
e abra http://127.0.0.1:8000/

Não importa nada do back-end (inosys/settings.py, apps, banco): serve os
arquivos de frontend/ como estão, em /mockup/, com a simulação ligada.
Quando as views do Django existirem, este arquivo deixa de ser necessário.
"""
from pathlib import Path

PASTA_FRONT = Path(__file__).resolve().parent

# Chave fixa só para a prévia local: não é usada em nenhum ambiente real.
SECRET_KEY = 'previa-local-do-front-end-nao-usar-em-producao'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = []
MIDDLEWARE = []
TEMPLATES = []
ROOT_URLCONF = 'frontend.previa_urls'
WSGI_APPLICATION = None

# Sem banco: a prévia não lê nem grava dados (os dados de exemplo estão nas telas).
DATABASES = {}

USE_TZ = True
