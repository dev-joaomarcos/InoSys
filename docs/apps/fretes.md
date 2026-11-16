# App `fretes`

Cadastro de entregadores, registro de entregas, cálculo do valor sugerido e destaque de divergência.

Requisitos cobertos: RF07 a RF11. Acesso: perfis `fretes`, `gestor` e `admin`.

## Models

### `Entregador`

| Campo | Observação |
| --- | --- |
| `nome` | Obrigatório |
| `contato` | Opcional, texto livre |
| `valor_por_km` | Decimal, mínimo 0,01 |
| `status` | `ativo` ou `inativo` |

### `Entrega`

| Campo | Observação |
| --- | --- |
| `entregador` | FK `PROTECT` |
| `usuario` | FK `PROTECT`. Quem registrou; definido na criação |
| `destino` | Obrigatório |
| `data` | Padrão: hoje |
| `distancia` | Decimal com 1 casa, mínimo 0,1 km. Informada à mão |
| `valor_sugerido` | Calculado no servidor; não editável |
| `valor_cobrado` | Opcional, ≥ 0 |
| `status` | `pendente`, `em_andamento` ou `concluida` |

Propriedades: `divergente`, `diferenca` (cobrado − sugerido) e `diferenca_abs`.

## Regras

### Valor sugerido (RF08)

`services.calcular_sugerido(distancia, valor_por_km)` = distância × valor por km, arredondado para centavos com meio para cima.

- É calculado ao criar a entrega.
- É recalculado na edição apenas se o entregador ou a distância mudarem.
- Mudar o `valor_por_km` de um entregador vale só para as próximas entregas. As já registradas mantêm o valor sugerido.

Enquanto a pessoa preenche o formulário, `entregas/valor-sugerido/` devolve o cálculo ao vivo. É só uma prévia: o valor gravado é sempre recalculado no servidor ao salvar.

### Divergência (RF12)

Uma entrega é divergente quando `valor_cobrado` foi informado e é diferente de `valor_sugerido`. Não há tolerância: um centavo de diferença conta. Entrega sem valor cobrado não é divergente.

### Edição e status (RF09, RF10)

Entregas podem ser editadas em qualquer status. Não há exclusão de entrega. O status é um campo do formulário, sem transição forçada.

### Entregadores

Desativados em vez de excluídos. O formulário de entrega lista só os ativos; ao editar uma entrega antiga, o entregador atual continua na lista mesmo se foi desativado.

## Telas e rotas

| Rota | View | O que faz |
| --- | --- | --- |
| `entregas/` | `entrega_lista` | Histórico com filtros por entregador, status e período (RF11) |
| `entregas/resumo/` | `entrega_resumo` | Indicadores: pendentes, em andamento, concluídas, divergências |
| `entregas/nova/` | `entrega_nova` | Registra entrega |
| `entregas/<id>/editar/` | `entrega_editar` | Edita entrega |
| `entregas/valor-sugerido/` | `valor_sugerido` | Trecho com a prévia do cálculo. Aceita vírgula decimal |
| `entregadores/` | `entregador_lista` | Lista com busca e status. Padrão: só ativos |
| `entregadores/novo/`, `<id>/editar/` | | Cadastro e edição |
| `entregadores/<id>/desativar/` e `/reativar/` | | Exclusão lógica |

Eventos HTMX: `fretesAtualizados` (entregas e resumo) e `entregadoresAtualizados`.

## Testes

`fretes/tests.py` cobre cálculo, arredondamento, recálculo na edição, divergência, filtros e permissões.
