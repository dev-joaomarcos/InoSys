# InoSys · front-end (mockups navegáveis)

Telas em HTML + Bootstrap 5.3.3 + HTMX 2.0.3, com dados de exemplo, para aprovar o
visual e os fluxos antes da conversão para templates Django. Nada aqui depende do back-end.

## Como testar

1. Abra a pasta `frontend/` no Explorer e dê **duplo clique** em `login.html`
   (ou direto em `selecao.html`). A pasta `assets/` precisa estar ao lado dos HTML.
2. **Não use o Live Server.** A simulação só roda em `file://` (`window.inosysMockup`).
3. É preciso internet: Bootstrap, ícones, HTMX e as fontes vêm por CDN.
4. **Trocar de perfil:** use o seletor "Perfil simulado" no rodapé da sidebar (ou no topo da
   seleção). O perfil fica salvo no navegador. Telas fora do perfil mostram um aviso de acesso.
5. **Ver os ganchos do HTMX:** acrescente `?htmx=1` à URL (ex.: `estoque.html?htmx=1`).
   Os elementos com `hx-*` ganham contorno tracejado e um painel lista todos; clique num item
   para rolar até ele. O `?htmx=1` é mantido ao navegar pela sidebar.
6. **Celular:** F12 → modo dispositivo (Ctrl+Shift+M). Abaixo de 992px a sidebar vira painel
   deslizante (botão ☰) e as tabelas rolam na horizontal.

Atalhos do login no mockup: qualquer usuário/senha entra; senha `erro` mostra a falha;
senha `temporaria` simula o primeiro acesso (troca obrigatória).

Cada tela tem seus próprios dados de exemplo: uma alteração feita em Materiais não aparece
em Movimentações, e recarregar a página volta tudo ao início. No Django tudo vem do banco.

## Telas

| Arquivo | Tela | Perfis | Requisitos |
|---|---|---|---|
| `login.html` | Entrar + ajuda (sem e-mail) | todos | RF01 |
| `troca-senha.html` | Troca obrigatória no 1º acesso | todos | Fase 1 |
| `selecao.html` | Seleção de dashboard | todos (cartões por perfil) | RF01 |
| `estoque.html` | Materiais, entrada/saída, alerta | Estoque, Gestor, Admin | RF02–RF05 |
| `estoque-movimentacoes.html` | Histórico de movimentações | Estoque, Gestor, Admin | RF03, RF04, RF06 |
| `fretes.html` | Entregas, valor sugerido, status | Fretes, Gestor, Admin | RF08–RF11 |
| `fretes-entregadores.html` | Entregadores | Fretes, Gestor, Admin | RF07 |
| `visao-geral.html` | Dashboard de visão geral | Gestor, Admin | app relatorios |
| `relatorios.html` | Relatórios em tela | Gestor, Admin | RF12 |
| `admin-usuarios.html` | Usuários, senha temporária, anonimização | Admin | RF13, RF15 |
| `admin-log.html` | Log de ações | Admin | RF14 |

## Endpoints sugeridos (ganchos HTMX)

As URLs são sugestões para combinar com o back-end. `__ID__`, `__PAGINA_ANTERIOR__` e
`__PROXIMA_PAGINA__` são marcadores. Listas: 20 itens por página, alvo = card inteiro (`outerHTML`).
Formulário salvo responde **204 + `HX-Trigger`** (o modal fecha sozinho); com erro, responde **200**
com o formulário e as mensagens.

| Método | URL | Gatilho | Alvo · troca | Django devolve |
|---|---|---|---|---|
| GET | `/estoque/materiais/` | filtros, paginação, `estoqueAtualizado` | `#card-materiais` · outerHTML | `_lista_materiais.html` |
| GET | `/estoque/materiais/resumo/` | `estoqueAtualizado` | `#resumo-estoque` · outerHTML | `_resumo_estoque.html` (alerta RF05 + indicadores) |
| GET/POST | `/estoque/materiais/novo/` | botão / envio | `#modal-material .modal-content` · innerHTML | `_form_material.html` / 204 + `estoqueAtualizado` |
| GET/POST | `/estoque/materiais/__ID__/editar/` | botão da linha / envio | `#modal-material .modal-content` · innerHTML | `_form_material.html` / 204 + `estoqueAtualizado` |
| GET/POST | `/estoque/materiais/__ID__/desativar/` · `/reativar/` | menu da linha / confirmar | `#modal-status-material .modal-content` · innerHTML | confirmação / 204 + `estoqueAtualizado` |
| GET/POST | `/estoque/movimentacoes/nova/?material=&tipo=` | botões / envio | `#modal-movimentacao .modal-content` · innerHTML | `_form_movimentacao.html` / 204 + `estoqueAtualizado` |
| GET | `/estoque/movimentacoes/` | filtros, paginação, `estoqueAtualizado` | `#card-movimentacoes` · outerHTML | `_lista_movimentacoes.html` |
| GET | `/fretes/entregas/` | filtros, paginação, `fretesAtualizados` | `#card-entregas` · outerHTML | `_lista_entregas.html` |
| GET | `/fretes/entregas/resumo/` | `fretesAtualizados` | `#resumo-fretes` · outerHTML | `_resumo_fretes.html` |
| GET/POST | `/fretes/entregas/nova/` | botão / envio | `#modal-entrega .modal-content` · innerHTML | `_form_entrega.html` / 204 + `fretesAtualizados` |
| GET/POST | `/fretes/entregas/__ID__/editar/` | botão da linha / envio | `#modal-entrega .modal-content` · innerHTML | `_form_entrega.html` / 204 + `fretesAtualizados` |
| GET | `/fretes/entregas/valor-sugerido/?entregador=&distancia=` | mudar entregador / digitar km | `#calculo-sugerido` · innerHTML | trecho com o valor sugerido |
| GET | `/fretes/entregadores/` | filtros, paginação, `entregadoresAtualizados` | `#card-entregadores` · outerHTML | `_lista_entregadores.html` |
| GET/POST | `/fretes/entregadores/novo/` · `/__ID__/editar/` | botão / envio | `#modal-entregador .modal-content` · innerHTML | `_form_entregador.html` / 204 + `entregadoresAtualizados` |
| GET/POST | `/fretes/entregadores/__ID__/desativar/` · `/reativar/` | menu da linha / confirmar | `#modal-status-entregador .modal-content` · innerHTML | confirmação / 204 + `entregadoresAtualizados` |
| GET | `/relatorios/movimentacoes/` | filtros | `#card-rel-movimentacoes` · outerHTML | `_relatorio_movimentacoes.html` |
| GET | `/relatorios/fretes/` | filtros | `#card-rel-fretes` · outerHTML | `_relatorio_fretes.html` |
| GET | `/usuarios/` | filtros, paginação, `usuariosAtualizados` | `#card-usuarios` · outerHTML | `_lista_usuarios.html` |
| GET/POST | `/usuarios/novo/` | botão / envio | `#modal-usuario .modal-content` · innerHTML | `_form_usuario.html` / **200** `_senha_temporaria.html` + `usuariosAtualizados` |
| GET/POST | `/usuarios/__ID__/editar/` | botão da linha / envio | `#modal-usuario .modal-content` · innerHTML | `_form_usuario.html` / 204 + `usuariosAtualizados` |
| GET/POST | `/usuarios/__ID__/nova-senha/` | botão da linha / confirmar | `#modal-nova-senha .modal-content` · innerHTML | confirmação / **200** `_senha_temporaria.html` + `usuariosAtualizados` |
| GET/POST | `/usuarios/__ID__/desativar/` · `/reativar/` | menu da linha / confirmar | `#modal-status-usuario .modal-content` · innerHTML | confirmação / 204 + `usuariosAtualizados` |
| GET/POST | `/usuarios/__ID__/anonimizar/` | menu da linha / confirmar | `#modal-anonimizar .modal-content` · innerHTML | confirmação / 204 + `usuariosAtualizados` |
| GET | `/log/` | filtros, paginação | `#card-log` · outerHTML | `_lista_log.html` |

Login, troca de senha, seleção e visão geral não usam HTMX: são páginas comuns do Django.

## Pendências para o grupo decidir

- **Log de ações:** `tb_log_acoes` não guarda *o que* foi alterado (tabela/registro), só quem, a ação e quando.
  A tela mostra só isso. Se quiserem a coluna "Registro", o modelo precisa de um campo a mais.
- **Anonimização (RF15):** a tela aplica só a usuários. Falta definir se vale também para
  entregadores (nome e contato são dados pessoais) e se o `usuario_nome_snapshot` do log também é anonimizado.
- **"Solicitar ajuda aos administradores":** hoje só abre instruções. Se for para registrar um pedido
  para o admin, falta definir onde ele fica guardado.
- **Divergência de valor:** qualquer diferença entre cobrado e sugerido conta. Se houver tolerância, avisar.
- **Gráficos da visão geral:** a biblioteca ainda não foi definida (pendência do README); a tela usa só indicadores e listas.
