# Deploy no Railway

Estado em 16/11/2026: o repositório está preparado. O que resta é feito no painel do Railway, com a conta do grupo. O deploy real ainda não foi executado; a preparação foi verificada localmente (testes, `check --deploy`, `collectstatic` e os comandos em banco limpo).

## O que o repositório já traz

| Item | Onde |
| --- | --- |
| Versão do Python | `.python-version` (3.14). Sem ele o builder usaria a versão padrão dele, mais antiga |
| Comandos de build, pré-deploy e start | `railway.json` |
| Configuração por variáveis de ambiente | `inosys/settings.py` com django-environ |
| PostgreSQL por `DATABASE_URL` | `settings.py`; driver psycopg 3 |
| Servidor de aplicação | gunicorn |
| Arquivos estáticos | WhiteNoise; `STATIC_ROOT = staticfiles/`; storage com manifesto e compressão |
| HTTPS atrás de proxy | `SECURE_PROXY_SSL_HEADER`; redirecionamento, cookies seguros e HSTS quando `DEBUG=False` |
| Administrador inicial | comando `criar_admin`, chamado no pré-deploy |
| Dados de demonstração | comando `popular_demo`, rodado à mão |

### O que acontece em cada deploy (`railway.json`)

| Etapa | Comando |
| --- | --- |
| Build | instala o `requirements.txt` e roda `python manage.py collectstatic --noinput` |
| Pré-deploy | `python manage.py migrate --noinput && python manage.py clearsessions && python manage.py criar_admin` |
| Start | `gunicorn inosys.wsgi:application --bind 0.0.0.0:$PORT` |

Se o pré-deploy falhar, a versão nova não entra no ar e a anterior continua respondendo. O `clearsessions` apaga do banco as sessões já vencidas. Um deploy não desloga quem está usando o sistema.

## Arquivos estáticos

Não há pasta para criar. Cada app guarda seus arquivos em `<app>/static/<app>/`. No build, `collectstatic` copia tudo para `staticfiles/`, gera nomes com hash (`estilos.653f0ded835d.css`) e versões comprimidas. O WhiteNoise serve essa pasta pelo próprio gunicorn.

Duas consequências:

1. **`collectstatic` é obrigatório.** Com o storage de manifesto, se ele não rodar, toda página responde erro 500.
2. **`collectstatic` precisa da `SECRET_KEY` no build**, porque o `settings.py` não tem valor padrão para ela. Defina a variável antes do primeiro build.

O sistema não tem upload de arquivos: não há `MEDIA_ROOT` nem volume para configurar.

Os mockups em `docs/arquivo/mockups-front/` não participam do deploy.

## Passo a passo

1. **Criar o projeto** no Railway e conectar o repositório do GitHub, escolhendo a branch da demo.
2. **Adicionar um PostgreSQL** ao projeto.
3. **Definir as variáveis** no serviço web, antes do primeiro build:

   | Variável | Valor |
   | --- | --- |
   | `SECRET_KEY` | Chave longa e aleatória, exclusiva da produção |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | Domínio público sem `https://` (ex.: `inosys.up.railway.app`) |
   | `CSRF_TRUSTED_ORIGINS` | Origem completa (ex.: `https://inosys.up.railway.app`) |
   | `DATABASE_URL` | Referência à variável do serviço Postgres (ex.: `${{Postgres.DATABASE_URL}}`) |
   | `ADMIN_USUARIO` | Nome de acesso do Administrador inicial (ex.: `admin`) |
   | `ADMIN_SENHA` | Senha do primeiro acesso. Será trocada obrigatoriamente no primeiro login |
   | `ADMIN_NOME` | Opcional. Nome de exibição; o padrão é "Administrador" |
   | `SESSAO_MINUTOS` | Opcional. Minutos sem uso até a sessão expirar; o padrão é 60 |

   Para gerar a chave: `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`.

4. **Gerar o domínio público** do serviço (Settings → Networking) e conferir `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` com ele.
5. **Fazer o deploy** e acompanhar os logs de build e de pré-deploy.
6. **Entrar com o Administrador** e trocar a senha.
7. **Carregar os dados de demonstração** (seção abaixo).
8. **Conferir** com a lista de verificação.

Depois do primeiro acesso, `ADMIN_SENHA` pode ser removida das variáveis. O `criar_admin` não recria nem altera um usuário que já existe.

## Administrador inicial: `criar_admin`

- Lê `ADMIN_USUARIO` e `ADMIN_SENHA` do ambiente.
- Cria o usuário com perfil Administrador e senha temporária, só se ele ainda não existir.
- Sem as variáveis, ou com o usuário já criado, não faz nada e termina com sucesso. Por isso pode ficar no pré-deploy para sempre.

## Dados de demonstração: `popular_demo`

Cria três usuários (`paula`, `fabio`, `gustavo`), 9 materiais, 25 movimentações, 4 entregadores e 20 entregas, com datas relativas ao dia em que roda. Os dados são fixos e batem com o [roteiro da demo](roteiro-demo.md).

- Só roda em banco sem materiais nem entregadores.
- A senha dos três usuários vem de `--senha` ou da variável `DEMO_SENHA`. Ela não fica no código.
- Com `--se-vazio`, sai sem erro quando o banco já tem dados ou a senha não foi definida.

Duas formas de rodar em produção:

| Forma | Como |
| --- | --- |
| Shell no serviço (recomendado) | Com o CLI do Railway ligado ao projeto, abrir um shell no serviço (`railway ssh`) e rodar `python manage.py popular_demo --senha "..."` |
| Pelo pré-deploy, uma vez | Definir `DEMO_SENHA` e acrescentar `&& python manage.py popular_demo --se-vazio` ao pré-deploy no `railway.json`. Depois do deploy, desfazer a alteração e apagar a variável |

Rode o comando no dia da demo ou na véspera: como as datas são relativas, dados carregados há semanas saem da janela de 30 dias da visão geral.

Para recomeçar do zero é preciso recriar o banco no Railway. O sistema não apaga registros.

## Conferência depois do deploy

- [ ] `/login/` abre com estilo e logo (prova que os estáticos estão sendo servidos)
- [ ] Login do admin funciona e exige troca de senha
- [ ] Salvar um material funciona (prova que CSRF e HTMX estão certos)
- [ ] Um usuário de cada perfil vê só os módulos dele
- [ ] `/visao-geral/` mostra dados
- [ ] `http://` redireciona para `https://`

## Problemas prováveis

| Sintoma | Causa provável |
| --- | --- |
| Build falha em `collectstatic` com erro de `SECRET_KEY` | Variável não definida antes do build |
| Build usa Python diferente de 3.14 | `.python-version` ausente na branch publicada |
| Erro 500 em todas as telas, "Missing staticfiles manifest entry" | `collectstatic` não rodou |
| Erro 400 "Bad Request" | Domínio fora de `ALLOWED_HOSTS` |
| Erro 403 ao salvar qualquer formulário | `CSRF_TRUSTED_ORIGINS` sem o domínio, ou sem `https://` |
| Redirecionamento infinito | Proxy não está enviando `X-Forwarded-Proto` |
| Ninguém consegue entrar | `ADMIN_USUARIO`/`ADMIN_SENHA` não definidos; ver o log do pré-deploy |
| Telas sem estilo, mas funcionando | CDN bloqueado na rede de quem acessa (Bootstrap, HTMX e fontes vêm de CDN) |
| Healthcheck falha e o deploy não sobe | Ver abaixo |

## Healthcheck

Não está configurado, de propósito. Com o `settings.py` atual ele falharia por dois motivos:

- a requisição chega com o host `healthcheck.railway.app`, que precisaria estar em `ALLOWED_HOSTS`;
- ela chega em HTTP, e `SECURE_SSL_REDIRECT` responde com redirecionamento em vez de 200.

Para ativar no futuro: criar uma rota simples (por exemplo `/saude/`), incluí-la em `SECURE_REDIRECT_EXEMPT`, liberar o host e acrescentar `healthcheckPath` ao `railway.json`.

## Backup (RNF10)

O requisito pede backup diário. No Railway isso depende dos backups do serviço Postgres, cuja disponibilidade varia com o plano. Confirmar o que o plano do grupo oferece; sem backup automático, a alternativa é um `pg_dump` agendado. Nada está configurado.

## Cuidados

- `SECRET_KEY` e senhas nunca entram no repositório.
- HSTS fica ligado por um ano quando `DEBUG=False`. Em domínio `*.up.railway.app` isso não traz problema; em domínio próprio, só mantenha se o site for ficar sempre em HTTPS.
- O banco local `db.sqlite3` não vai para produção. O Postgres começa vazio.
- `python manage.py check --deploy` ainda mostra três avisos (subdomínios e preload do HSTS, e tamanho da chave quando ela é fraca). Nenhum impede a demo.
