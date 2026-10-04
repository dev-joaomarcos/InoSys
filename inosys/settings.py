"""
Configurações do Django para o projeto InoSys.

Gerado por 'django-admin startproject' com o Django 6.1.1.

Os valores que mudam de ambiente para ambiente (chave secreta, DEBUG, hosts,
banco de dados) NÃO ficam aqui: são lidos de variáveis de ambiente ou do
arquivo `.env` na raiz do projeto. Use o `.env.example` como modelo.

Documentação:
- Visão geral: https://docs.djangoproject.com/en/6.1/topics/settings/
- Lista completa de configurações: https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path

import environ

# Raiz do projeto (a pasta que contém o manage.py).
# Use BASE_DIR / 'subpasta' para montar caminhos a partir dela.
BASE_DIR = Path(__file__).resolve().parent.parent

# Leitura de variáveis de ambiente com django-environ.
# Cada entrada abaixo define o tipo e o valor padrão usado quando a variável
# não existe: DEBUG desligado e listas vazias (mais seguro por padrão).
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)
# Carrega o arquivo .env, se existir. Variáveis já definidas no ambiente real
# (como as configuradas no Railway) têm prioridade sobre o conteúdo do .env.
environ.Env.read_env(BASE_DIR / '.env')


# ---------------------------------------------------------------------------
# Segurança e ambiente
# Checklist de deploy: https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
# ---------------------------------------------------------------------------

# ATENÇÃO: mantenha a chave secreta de produção em segredo.
# Não há valor padrão de propósito: se SECRET_KEY faltar, o projeto não sobe.
SECRET_KEY = env('SECRET_KEY')

# ATENÇÃO: nunca deixe DEBUG=True em produção (expõe código e configurações
# nas páginas de erro). Controlado pela variável de ambiente DEBUG.
DEBUG = env('DEBUG')

# Domínios que podem servir o app, sem esquema (ex.: seu-app.up.railway.app).
# Com DEBUG=False e a lista vazia, toda requisição recebe erro 400.
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Origens confiáveis para requisições POST (proteção CSRF). Aqui o esquema é
# obrigatório (ex.: https://seu-app.up.railway.app).
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')

# Configurações de HTTPS: só ficam ativas fora do modo DEBUG, para não
# atrapalhar o desenvolvimento local em http://localhost.
# O Railway termina o HTTPS no proxy e repassa o protocolo original no header
# X-Forwarded-Proto; sem esta linha o Django acharia que toda requisição é HTTP
# e entraria em loop de redirecionamento.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG      # redireciona http -> https
SESSION_COOKIE_SECURE = not DEBUG    # cookie de sessão só trafega por HTTPS
CSRF_COOKIE_SECURE = not DEBUG       # cookie CSRF só trafega por HTTPS
# HSTS: o navegador passa a exigir HTTPS neste domínio pelo tempo (em segundos)
# definido em SECURE_HSTS_SECONDS. O padrão é 1 hora, para o primeiro deploy: o
# navegador guarda esse valor e não dá para desfazer antes do prazo. Depois de
# validar o HTTPS, suba pela variável de ambiente (86400 = 1 dia,
# 2592000 = 30 dias). Em DEBUG fica 0, para não prender o localhost em HTTPS.
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=3600) if not DEBUG else 0


# ---------------------------------------------------------------------------
# Aplicações
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Apps do próprio Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps do InoSys
    'contas.apps.ContasConfig',            # autenticação, perfis, permissões e log de ações
    'estoque.apps.EstoqueConfig',          # materiais, entradas, saídas e alertas de reposição
    'fretes.apps.FretesConfig',            # entregadores, entregas e valor sugerido por km
    'relatorios.apps.RelatoriosConfig',    # dashboard e relatórios (único que lê dados dos outros apps)
]

# A ordem importa: cada middleware envolve os que vêm depois dele.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serve os arquivos estáticos direto do Django (sem nginx).
    # Precisa vir logo depois do SecurityMiddleware e antes dos demais.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Módulo com as rotas principais do projeto.
ROOT_URLCONF = 'inosys.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pastas extras de templates (globais ao projeto). Vazio por enquanto:
        # os templates ficam dentro de cada app (APP_DIRS).
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            # Variáveis disponíveis automaticamente em todo template.
            # Os três abaixo são exigidos pelo admin do Django.
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Ponto de entrada WSGI, usado pelo gunicorn em produção.
WSGI_APPLICATION = 'inosys.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
# ---------------------------------------------------------------------------

# Com DATABASE_URL definida (ex.: postgres://usuario:senha@host:5432/banco),
# usa esse banco, que é o caso do PostgreSQL em produção. Sem ela, cai no
# SQLite local (arquivo db.sqlite3, ignorado pelo git), suficiente para dev.
database_url = env('DATABASE_URL', default=None)
if database_url:
    DATABASES = {'default': env.db_url_config(database_url)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------------------------------------------------------------------------
# Autenticação
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators
# ---------------------------------------------------------------------------

# Rota de login e destino padrão após autenticar. A tela de login ainda será
# criada no app `contas`; até lá, @login_required não terá para onde redirecionar.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'

# Regras aplicadas ao definir ou alterar senhas (formulários do Django e admin).
AUTH_PASSWORD_VALIDATORS = [
    {
        # Impede senha parecida com dados do usuário (nome, e-mail etc.).
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Exige tamanho mínimo (8 caracteres por padrão).
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Bloqueia senhas comuns, como "12345678" ou "password".
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Bloqueia senhas formadas apenas por números.
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------------------------------------
# Internacionalização
# https://docs.djangoproject.com/en/6.1/topics/i18n/
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'pt-br'              # idioma das mensagens do Django e do admin
TIME_ZONE = 'America/Sao_Paulo'      # fuso usado na exibição de datas e horas
USE_I18N = True                      # habilita a tradução de textos
USE_TZ = True                        # guarda datas em UTC no banco e converte ao exibir


# ---------------------------------------------------------------------------
# Arquivos estáticos (CSS, JavaScript, imagens do sistema)
# https://docs.djangoproject.com/en/6.1/howto/static-files/
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'                    # prefixo da URL pública dos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'    # destino do `collectstatic` (ignorado pelo git)

STORAGES = {
    # Armazenamento de uploads. Sem uso por enquanto (fotos de entrega estão
    # fora do escopo do MVP).
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    # WhiteNoise comprime os arquivos e adiciona hash ao nome (cache longo no
    # navegador). Com DEBUG=False exige rodar `python manage.py collectstatic`
    # antes; do contrário, o {% static %} gera erro.
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ---------------------------------------------------------------------------
# E-mail
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
# ---------------------------------------------------------------------------

# O sistema não envia e-mails (senhas temporárias são geradas pelo
# Administrador e exibidas em tela). O backend de console apenas imprime
# qualquer e-mail no terminal, o que serve para desenvolvimento.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


# ---------------------------------------------------------------------------
# Logs
# https://docs.djangoproject.com/en/6.1/topics/logging/
# ---------------------------------------------------------------------------

# Envia os logs para o console (stdout). No Railway, tudo que sai no stdout
# aparece na aba de logs do serviço.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
