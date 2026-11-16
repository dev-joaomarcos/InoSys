# InoSys: instruções para agentes de IA

Este arquivo vale para qualquer agente (Claude Code, Codex, Cursor etc.) e para qualquer membro do grupo. O `CLAUDE.md` apenas importa este arquivo; edite sempre aqui.

## O projeto

Sistema web interno da INOVE Divisórias e Forros: controle de estoque e monitor financeiro de fretes. Projeto acadêmico (PIM IV, ADS/USCS) em preparação para demo.

Monólito Django 6.1 (Python 3.14) renderizado no servidor, com Bootstrap 5.3.3 e HTMX 2.0.3. PostgreSQL em produção, SQLite local. Deploy no Railway.

## Leia antes de mexer

| Vai mexer em... | Leia |
| --- | --- |
| Qualquer coisa | `docs/arquitetura.md` |
| Um app | `docs/apps/<app>.md` |
| Template, CSS ou HTMX | `docs/frontend.md` |
| Settings, dependências, deploy | `docs/deploy-railway.md` |
| Algo que parece faltar ou estar errado | `docs/pendencias.md` (pode ser decisão em aberto) |

## Comandos

```bash
python manage.py runserver
python manage.py test                 # obrigatório antes de concluir uma tarefa
python manage.py test <app>
python manage.py makemigrations && python manage.py migrate
python manage.py check --deploy
python manage.py criar_admin          # admin inicial a partir de ADMIN_USUARIO / ADMIN_SENHA
python manage.py popular_demo --senha <senha>   # dados de demonstração, só em banco vazio
```

Ambiente virtual em `.venv`. No Windows: `.venv\Scripts\Activate.ps1`.

## Regras que não podem ser quebradas

1. **Saldo de estoque** (`Material.qtd_atual`) só muda em `estoque.services.registrar_movimentacao`.
2. **Movimentação é imutável**: sem edição e sem exclusão.
3. **Sem exclusão física** de material, entregador, usuário ou entrega. Desative.
4. **Valor sugerido** é calculado no servidor por `fretes.services.calcular_sugerido`. Nunca confie no valor vindo do navegador.
5. **Toda view de módulo** leva `@perfil_requerido(...)` com as constantes de `contas/permissoes.py`.
6. **Toda criação ou edição** chama `contas.logs.registrar_log`.
7. **Dependência entre apps**: `estoque` e `fretes` não se importam; só `relatorios` importa os dois; todos podem importar `contas`.
8. **Segredos fora do Git**: nunca leia, imprima ou versione o `.env`.

## Convenções

- Português no código de domínio, nos comentários, nas mensagens ao usuário e nos commits.
- Views de função. Regra de negócio com transação ou cálculo vai em `services.py`.
- HTMX: use `contas/htmx.py`. Formulário salvo responde 204 com `HX-Trigger`; com erro, 200 com o formulário.
- Templates: página inteira em `tela.html`, trecho em `_trecho.html`.
- CSS: só variáveis `--is-*`; classe nova com prefixo `is-` em `contas/static/inosys/estilos.css`; nada de `style` com valor solto.
- Alertas (`.alert`) e badges (`.is-badge`) recebem o ícone de status pelo CSS. Não ponha `<i class="bi">` no começo de um alerta.
- `docs/arquivo/` é material arquivado: não use como referência e não edite.
- Paginação de 20 itens com o `Paginator` do Django.
- Não adicione dependência sem pedir. Não troque Bootstrap ou HTMX por outra coisa.
- Mudança de regra vem com teste.

## Escopo

Não invente campo, tela, módulo ou fluxo. Estão fora do MVP: envio de e-mail, upload de arquivos e fotos, exportação de relatórios, cálculo automático de distância e autocadastro. Se a tarefa parecer exigir algo assim, pergunte antes.

## Documentação

- Mudou comportamento, atualize o documento correspondente em `docs/` no mesmo commit.
- Não crie arquivos Markdown soltos em outras pastas. Documentação vive em `docs/`; instruções para agentes vivem aqui.
- Decisão nova em aberto entra em `docs/pendencias.md`.

## Git

- Não faça commit nem push sem pedido explícito.
- Não trabalhe direto na `main`.
- Não reescreva histórico compartilhado (`push --force`, `reset --hard` em branch remota).
