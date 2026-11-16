# Desenvolvimento

## Rodar local

Pré-requisito: Python 3.14.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env         # depois troque a SECRET_KEY
python manage.py migrate
python manage.py createsuperuser    # cria o Administrador inicial (perfil admin)
python manage.py runserver
```

Abra http://127.0.0.1:8000/ e entre com o superusuário.

Para ter dados de exemplo em um banco recém-criado (usuários `paula`, `fabio` e `gustavo`, materiais, movimentações e entregas):

```powershell
python manage.py popular_demo --senha "uma-senha-de-teste"
```

O comando só roda se ainda não houver materiais nem entregadores.

Sem `DATABASE_URL` no `.env`, o banco é o arquivo `db.sqlite3` (fora do Git). Para usar PostgreSQL local, acrescente `DATABASE_URL=postgres://usuario:senha@localhost:5432/inosys`.

Mantenha `DEBUG=True` no `.env` local. Com `DEBUG=False`, o Django redireciona tudo para HTTPS e o `runserver` deixa de responder.

## Testes

```powershell
python manage.py test               # tudo (106 testes)
python manage.py test estoque       # um app
python manage.py test fretes.tests.NomeDaClasse.test_algo
```

Rode a suíte antes de cada push. Mudança de regra de negócio vem com teste.

## Convenções

- **Idioma.** Código de domínio, comentários, mensagens e commits em português.
- **Views de função** com `@perfil_requerido(...)` e, quando aceitam formulário, `@require_http_methods(["GET", "POST"])`.
- **Regra de negócio em `services.py`** quando envolve transação, cálculo ou mais de um model. A view fica com filtro, paginação e resposta.
- **Log manual.** Toda criação ou edição chama `registrar_log(request.user, LogAcao.CRIACAO | EDICAO)`.
- **Sem exclusão física** de material, entregador, usuário, movimentação ou entrega.
- **HTMX.** Use os helpers de `contas/htmx.py` e o contrato descrito em [frontend.md](frontend.md).
- **Templates.** Página inteira em `tela.html`; trecho começa com `_`.
- **Paginação** de 20 itens com o `Paginator` do Django.
- **Dependências.** Não acrescente biblioteca sem combinar com o grupo. Versões fixas no `requirements.txt`.
- **Migrações.** Gere com `makemigrations` e inclua no mesmo commit do model.

## Fluxo de Git

- `main` é a base estável. A branch de preparação da demo parte de `Murilo-Back`.
- Trabalhe em branch própria e abra pull request.
- Nunca inclua `.env`, `db.sqlite3` ou `staticfiles/` no commit (já estão no `.gitignore`).
