# App `estoque`

Cadastro de materiais, entradas e saídas, alerta de estoque baixo e histórico.

Requisitos cobertos: RF02 a RF06, RNF02. Acesso: perfis `estoque`, `gestor` e `admin`.

## Models

### `Material`

| Campo | Observação |
| --- | --- |
| `nome` | Obrigatório |
| `descricao` | Opcional |
| `unidade_medida` | Texto curto (un, m², cx) |
| `quantidade_minima` | Inteiro ≥ 0. Dispara o alerta |
| `qtd_atual` | Saldo. Começa em 0 e só muda por movimentação |
| `status` | `ativo` ou `inativo` |

- `Material.objects.ativos()` devolve os ativos.
- `Material.objects.baixos()` devolve os ativos com `qtd_atual < quantidade_minima` (RF05). Saldo igual ao mínimo não é estoque baixo.
- Propriedades: `esta_ativo`, `esta_baixo`.

### `Movimentacao`

| Campo | Observação |
| --- | --- |
| `material` | FK `PROTECT` |
| `usuario` | FK `PROTECT`. Quem registrou |
| `tipo` | `entrada` ou `saida` |
| `quantidade` | Inteiro ≥ 1 |
| `data` | Padrão: hoje |
| `motivo` | Só em saída: `uso_producao`, `perda_dano`, `ajuste_inventario` |

Movimentação é imutável. Não há tela de edição ou exclusão, e o admin do Django bloqueia inclusão, alteração e remoção.

## Regra central: `services.registrar_movimentacao`

Único ponto que altera `qtd_atual`. Em uma transação:

1. Trava a linha do material com `select_for_update`, para que duas saídas simultâneas não passem do saldo.
2. Recusa material desativado.
3. Recusa saída maior que o saldo, com a mensagem "Saldo insuficiente: há N un em estoque."
4. Soma ou subtrai de `qtd_atual`.
5. Grava a `Movimentacao`. O motivo é descartado em entradas.
6. Registra log de criação.

Qualquer código novo que mexa no saldo deve passar por essa função.

## Telas e rotas

| Rota | View | O que faz |
| --- | --- | --- |
| `materiais/` | `material_lista` | Lista com busca, filtro de situação (baixo/normal) e de status. Padrão: só ativos |
| `materiais/resumo/` | `material_resumo` | Trecho com o alerta de estoque baixo e os indicadores |
| `materiais/novo/` | `material_novo` | Cadastra com saldo 0 |
| `materiais/<id>/editar/` | `material_editar` | Edita nome, descrição, unidade e mínimo. Não edita o saldo |
| `materiais/<id>/desativar/` e `/reativar/` | | Exclusão lógica; o histórico é mantido |
| `movimentacoes/` | `movimentacao_lista` | Histórico com filtros por material, tipo e período (RF06) |
| `movimentacoes/nova/` | `movimentacao_nova` | Formulário de entrada ou saída. Aceita `?tipo=` e `?material=` para já vir preenchido |

Listas paginam em 20 itens. O evento HTMX do módulo é `estoqueAtualizado`: a lista de materiais, o resumo e o histórico escutam e se recarregam.

## Validações (`forms.py`)

- `MaterialForm`: nome e unidade obrigatórios, mínimo inteiro ≥ 0.
- `MovimentacaoForm`: só lista materiais ativos; quantidade ≥ 1; saída exige motivo.

## Testes

`estoque/tests.py` cobre CRUD, entrada, saída, saldo insuficiente, alerta, filtros e permissões.
