# App `relatorios`

Painel de visão geral e relatórios em tela. Não tem models: só lê dados de `estoque` e `fretes`.

Requisitos cobertos: RF12, RNF01. Acesso: perfis `gestor` e `admin`.

## Telas e rotas

| Rota | View | O que faz |
| --- | --- | --- |
| `/visao-geral/` | `visao_geral` | Painel com indicadores, listas curtas e gráfico |
| `/relatorios/` | `relatorios` | Página com duas abas: movimentações e fretes |
| `/relatorios/movimentacoes/` | `relatorio_movimentacoes` | Trecho da aba (HTMX) ou página inteira com a aba aberta (URL direta) |
| `/relatorios/fretes/` | `relatorio_fretes` | Idem para fretes |

## Agregações (`services.py`)

### `resumo_geral()`: visão geral

Período fixo: últimos 30 dias (`DIAS_PADRAO`).

| Dado | Regra |
| --- | --- |
| Estoque baixo | Contagem e os 8 materiais mais abaixo do mínimo. Independe do período |
| Entregas em aberto | Pendentes e em andamento; contagem e as 5 mais recentes. Independe do período |
| Concluídas e total cobrado | Entregas concluídas no período |
| Divergências | Contagem e as 5 mais recentes no período |
| Gráfico | Sugerido × cobrado por entregador, só com entregas concluídas que têm valor cobrado |

O gráfico é feito em HTML e CSS (barras com altura em porcentagem). Não há biblioteca de gráficos.

### `relatorio_movimentacoes(material_id, inicio, fim)`

Uma linha por material com: entradas, saídas separadas por motivo (uso em produção, perda ou dano, ajuste de inventário), número de movimentações, saldo atual e marcador de estoque baixo.

### `relatorio_fretes(entregador_id, status, inicio, fim, so_divergencias)`

- Resumo por entregador: entregas, km, total sugerido, total cobrado e diferença. A diferença considera só entregas com valor cobrado informado.
- Linha de total.
- Tabela de entregas limitada a 500 linhas (`LIMITE_ENTREGAS`), com aviso quando o filtro passa do limite. É o que mantém a resposta rápida (RNF01).

## Filtros de período

- Sem parâmetro na URL: últimos 30 dias.
- Parâmetro presente e vazio ou inválido: sem limite de data.

## Limites atuais

- Relatórios só em tela; não há exportação.
- Sem paginação nos relatórios; o teto de 500 linhas faz esse papel.

## Testes

`relatorios/tests.py` cobre agregações, filtros, limite e permissões.
