# InoSys

Gestor de estoque e monitor financeiro de fretes para a INOVE Divisórias e Forros.

Sistema web com dois módulos: controle de estoque, com saldo atualizado automaticamente e alerta de reposição, e monitoramento de fretes, com cálculo do valor sugerido por quilômetro e destaque das divergências. Desenvolvido como Projeto Integrado Multidisciplinar (PIM IV) do curso de Análise e Desenvolvimento de Sistemas da USCS.

O escopo do MVP está implementado e em preparação para a demo. O que ficou em aberto está em [docs/pendencias.md](docs/pendencias.md).

## Documentação

| Para... | Leia |
| --- | --- |
| Entender o sistema sem termos técnicos | [docs/visao-simples.md](docs/visao-simples.md) |
| Entender a arquitetura | [docs/arquitetura.md](docs/arquitetura.md) |
| Desenvolver | [docs/desenvolvimento.md](docs/desenvolvimento.md) |
| Publicar no Railway | [docs/deploy-railway.md](docs/deploy-railway.md) |
| Apresentar a demo | [docs/roteiro-demo.md](docs/roteiro-demo.md) |
| Ver tudo | [docs/README.md](docs/README.md) |

Quem usa agente de IA (Claude Code, Codex, Cursor): as regras do projeto estão em [AGENTS.md](AGENTS.md).

## Stack

| Item | Versão |
| --- | --- |
| Python | 3.14 |
| Django | 6.1.1 |
| Banco | PostgreSQL em produção; SQLite local |
| Front | Templates Django + Bootstrap 5.3.3 + HTMX 2.0.3 |
| Hospedagem | Railway (gunicorn + WhiteNoise) |

## Rodar local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env         # depois troque a SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py popular_demo --senha "uma-senha-de-teste"   # opcional: dados de exemplo
python manage.py runserver
```

Abra http://127.0.0.1:8000/. Testes: `python manage.py test`.

## Apps

| App | Responsabilidade |
| --- | --- |
| `contas` | Autenticação, perfis, permissões, administração de usuários e log de ações |
| `estoque` | Materiais, entradas, saídas, alerta de estoque baixo e histórico |
| `fretes` | Entregadores, entregas, valor sugerido e histórico |
| `relatorios` | Visão geral e relatórios; é o único que lê dados dos outros módulos |

## Perfis de usuário

| Perfil | Acesso |
| --- | --- |
| Operacional de Estoque | Módulo de estoque |
| Operacional de Fretes | Módulo de fretes |
| Gestor | Os dois módulos, visão geral e relatórios |
| Administrador | Tudo, mais gestão de usuários, log de ações e anonimização |

Não há autocadastro. O Administrador cadastra cada usuário e o sistema gera uma senha temporária, exibida uma única vez; no primeiro acesso a troca é obrigatória.
