# Front-end

O front é renderizado pelo Django. Não há framework JS nem build: são templates, um CSS próprio sobre o Bootstrap e HTMX para atualizar partes da página.

## Onde fica cada coisa

| Item | Local |
| --- | --- |
| Layout base (sidebar, topo, scripts) | `contas/templates/inosys/base_app.html` |
| CSS do sistema | `contas/static/inosys/estilos.css` |
| Logos | `contas/static/inosys/img/` |
| JS comum a todas as telas | `contas/static/inosys/app.js` |
| JS por tela | `<app>/static/<app>/*.js` |
| Telas | `<app>/templates/<app>/tela.html` |
| Trechos HTMX | `<app>/templates/<app>/_trecho.html` |

Login, troca de senha e apresentação não herdam do `base_app.html`: têm HTML próprio e carregam os mesmos CDNs.

Dependências externas, todas por CDN: Bootstrap 5.3.3 (CSS e JS), Bootstrap Icons 1.11.3, HTMX 2.0.3 e as fontes IBM Plex (Google Fonts, importadas no `estilos.css`). Sem internet, as telas perdem o estilo.

## Contrato HTMX

| Situação | Resposta do servidor | Efeito na tela |
| --- | --- | --- |
| Lista (filtro, paginação, evento) | Trecho `_lista_*.html` | Troca o card inteiro (`outerHTML`) |
| Abrir formulário | Trecho `_form_*.html` | Preenche `.modal-content` |
| Formulário salvo | **204** + `HX-Trigger` com o evento e a mensagem | Modal fecha, listas recarregam, aviso aparece |
| Formulário com erro | **200** com o formulário e as mensagens | Modal mostra os erros |
| Senha temporária gerada | **200** com `_senha_temporaria.html` + `HX-Trigger` | Modal mostra a senha; a lista recarrega |
| Sessão expirada ou sem login | **401** + `HX-Redirect` para o login | A página inteira vai para o login e depois volta à tela atual |
| Senha temporária pendente | **403** + `HX-Redirect` para a troca de senha | A página inteira vai para a troca de senha |

Eventos: `estoqueAtualizado`, `fretesAtualizados`, `entregadoresAtualizados`, `usuariosAtualizados`.

Helpers em `contas/htmx.py`:

- `pagina_ou_trecho(request, pagina, trecho, contexto)` devolve o trecho para pedidos HTMX e a página inteira para acesso direto ou volta no histórico. Por isso toda URL de lista funciona se for colada no navegador.
- `salvo(evento, mensagem)` monta o 204 com `HX-Trigger`.
- `gatilho(resposta, evento)` acrescenta o evento a uma resposta existente.
- `ir_para(url)` responde com `HX-Redirect`, para quando o pedido de um trecho precisa virar navegação da página inteira.

Todos os apps importam esses helpers; nenhum tem cópia própria.

O token CSRF vai em todas as requisições HTMX por `hx-headers` no `<body>`.

No navegador, o `app.js` cuida do lado de lá do contrato:

- abre o modal de um botão com `data-abrir-modal` (na hora, ou depois da troca de conteúdo quando o botão tem `hx-get`);
- fecha o modal quando a resposta é 204;
- mostra a mensagem do `HX-Trigger` como aviso flutuante. Evento novo precisa entrar na lista de eventos do `app.js`;
- marca o item ativo do menu a partir do `data-modulo` do `<body>`;
- expõe `window.inosys` (`formatar.numero`, `formatar.moeda`, `toast`, `abrirModal`, `fecharModal`) para os scripts de cada tela.

## Regras de estilo

Fonte: design system. Resumo do que vale no código:

1. Cor, fonte, raio e sombra vêm das variáveis `--is-*`. Nada de `style="..."` com valor solto.
2. Use os componentes do Bootstrap, já reestilizados. Classe nova leva o prefixo `is-` e entra no `estilos.css`.
3. Status sempre com palavra, nunca só cor.
4. Rótulo de campo sempre visível.
5. Números à direita e em IBM Plex Mono. Datas `29/09/2026`, moeda `R$ 1.234,56`.
6. Textos em português, ações no imperativo, sem emoji e sem exclamação.
7. Abaixo de 992px a sidebar vira painel deslizante; tabelas rolam na horizontal.

## Alertas e badges

O estado nunca depende só da cor: cada status combina cor, textura ou estilo de borda, ícone e palavra. O ícone é posto pelo CSS (`::before` com a fonte do Bootstrap Icons), então o HTML fica simples.

### Alertas: trilho de ícone

```html
<div class="alert alert-warning" role="status">
  <strong>3 materiais abaixo da quantidade mínima:</strong> ...
</div>
```

Um bloco de 40px à esquerda (o trilho) carrega o ícone e a textura. O texto fica sobre fundo liso, com borda de 1px igual nos quatro lados.

| Classe | Uso | Textura do trilho | Ícone |
| --- | --- | --- | --- |
| `alert-success` | Operação concluída; avisos flutuantes | lisa | `check-circle` |
| `alert-info` (ou só `alert`) | Informação | pontos | `info-circle` |
| `alert-warning` | Atenção: estoque baixo, senha exibida uma vez | hachura diagonal | `exclamation-triangle` |
| `alert-danger` | Erro ou ação irreversível | linhas horizontais | `x-octagon` |

Não ponha `<i class="bi">` no começo do alerta: o ícone apareceria duas vezes. O mesmo vale para os avisos flutuantes (`inosys.toast`).

### Badges

```html
<span class="is-badge is-badge-warning">Pendente</span>
```

| Classe | Borda | Ícone | Uso no sistema |
| --- | --- | --- | --- |
| `is-badge-success` | contínua | `check` | Concluída, Ativo, Normal |
| `is-badge-info` | pontilhada | `circle-fill` | Em andamento, Gestor, Entrada |
| `is-badge-warning` | tracejada + hachura suave | `exclamation-triangle-fill` | Pendente, Estoque baixo, senha temporária |
| `is-badge-danger` | dupla | `x` | Divergência de valor |
| `is-badge-neutral` | contínua cinza | `dash` | Desativado, Saída, ações do log |
| `is-badge-dark` | contínua navy | `square-fill` | Administrador, Anonimizado |

Se o badge já traz um ícone próprio (`<i class="bi bi-box-arrow-up">` em "Saída", por exemplo), o ícone padrão do status não é acrescentado.

## Apresentação (landing page)

Template `contas/templates/contas/apresentacao.html`, página pública sem sidebar e sem JavaScript próprio. As classes ficam na seção 12 do `estilos.css`, com o prefixo `is-lp-`.

| Parte | Classes | Observação |
| --- | --- | --- |
| Abertura em navy | `is-lp-abertura`, `is-lp-topo`, `is-lp-heroi` | A captura da abertura desce além do navy e pousa sobre o fundo da página |
| Captura em moldura | `is-lp-tela` | Sempre com `width`, `height` e texto alternativo descritivo |
| Blocos de funcionalidade | `is-lp-bloco`, `is-lp-bloco-invertido` | Texto de um lado e tela real do outro, alternando |
| Passos numerados | `is-lp-passos` | A numeração vem do CSS (`counter`) |

Abaixo de 992px os blocos empilham; abaixo de 576px os passos e os dois problemas ficam em uma coluna.

### Capturas de tela

Ficam em `contas/static/inosys/img/telas/` (estoque, fretes, visão geral e relatórios), em PNG de 1280 × 800. Foram feitas com os dados do `popular_demo`, logado como gestor, e as datas ficam fixas no dia da captura.

Para refazer depois de uma mudança visual: subir o sistema com um banco recém-populado pelo `popular_demo`, entrar como `gustavo`, deixar a janela em 1280 × 800 com o navegador em português e capturar `/estoque/materiais/?status=`, `/fretes/entregas/`, `/visao-geral/` e `/relatorios/fretes/`.

## Design system: v1, v2 e o que está implementado

- **v1**: `docs/arquivo/mockups-front/INOSYS-DESIGN-SYSTEM.md`. Arquivado. Foi a base do CSS.
- **v2**: [INOSYS-DESIGN-SYSTEM.html](INOSYS-DESIGN-SYSTEM.html). Documento navegável, com pré-visualização dos componentes. Está na versão 2.1, de 16/11/2026. O arquivo se chamava `INOSYS-DESIGN-SYSTEM-SHADCN.html`.
- **Implementado**: `contas/static/inosys/estilos.css`. Quando houver divergência, o CSS vence.

O v2 é uma página de documentação. O CSS embutido nela estiliza a própria página, com nomes de classe e de variável diferentes (`.bd`, `.al`, `--brand`, `--fg`), e não é um `estilos.css` pronto para copiar. Quem mudar um componente no `estilos.css` precisa repetir a mudança no CSS embutido do HTML.

### Onde o sistema coincide com o v2

Paleta e tokens do tema claro, tipografia, raios, sombra, sidebar, modal com fundo navy, KPIs, marcador de linha em alerta (`is-row-alert`), alertas, badges, estados do HTMX, contrato 204/200, breakpoints e as 11 telas.

### O que mudou do v2 para o v2.1

O v2 original foi revisado em dois componentes, no sistema e no documento:

| Item | No v2 original | No v2.1 e no sistema | Motivo |
| --- | --- | --- | --- |
| Alertas | Faixa lateral de 7px com `border-style` por status e fundo tingido | Trilho de ícone de 40px com textura; texto em fundo liso | A faixa renderizava de forma desigual (poucos traços, cortados nos cantos; o de erro tinha 8px) e tinha aparência genérica. O trilho tem a mesma geometria em todos os status e mantém a textura |
| Símbolos de status | Unicode (✓ ● ▲ ✕ – ■) | Bootstrap Icons | Coerência com o resto das telas, que já usam essa família |
| Hachura do badge de atenção | Mais forte | Mais suave | A hachura competia com o texto |

Uma diferença restante: no documento, o badge escuro (Administrador) tem fundo navy sólido e texto branco; no sistema, fundo navy translúcido e texto navy. A versão do documento é a que funciona no tema escuro.

### O que o v2 traz e o sistema ainda não tem

| Item do v2 | Situação | Observação |
| --- | --- | --- |
| Tema escuro via `data-bs-theme="dark"` | Não implementado | Toca todas as telas; fica para depois da demo |
| Gráficos com padrão além da cor | Barras sólidas em duas cores | Só CSS; baixo esforço |
| Gráfico "Entradas e saídas de estoque" | Não existe | Funcionalidade nova: exige agregação em `relatorios.services` |
| Barra de progresso e card selecionável | Sem CSS e sem tela que use | Referência para funcionalidades futuras |

### Exemplos que vão além do sistema atual

Alguns exemplos do documento mostram coisas que o sistema não tem: campo "SKU", "Manter conectado", "Enviar relatório por e-mail", capacidade de depósito e de caminhão, barra de progresso e card selecionável. Eles estão ali de propósito, como referência visual para possíveis funcionalidades novas. Não são requisito: nenhum deles deve ser implementado sem decisão do grupo.

## Mockups arquivados

As 11 telas em HTML estático que serviram para aprovar o visual estão em [arquivo/mockups-front/](arquivo/README.md). Não são servidas em produção e o CSS delas ficou congelado antes dos alertas e badges atuais.

O antigo `sidebar.js` do sistema, que carregava junto o código de simulação dos mockups, foi substituído pelo `app.js`. A versão original continua na pasta arquivada.
