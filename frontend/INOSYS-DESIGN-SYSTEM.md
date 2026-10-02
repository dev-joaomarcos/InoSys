# InoSys — Design System

Sistema de gestão de estoque e monitor financeiro de fretes da **INOVE Divisórias e Forros** (PIM IV, ADS/USCS).
Interface web interna, usada no dia a dia por quatro perfis. Stack do front: HTML + **Bootstrap 5.3.3** + **HTMX** + Bootstrap Icons, fonte **IBM Plex**.

![Logo InoSys](assets/img/logo-inosys.png)

Este documento é **só o design system**: marca, cores, tipografia, forma, componentes, padrões e estados.
Telas, regras de negócio e endpoints ficam fora. O CSS completo está no **Apêndice A** e os arquivos da logo
vão junto (pasta `assets/img/`).

---

## Para o Claude Code: como usar este documento

1. Crie `assets/estilos.css` com o conteúdo **exato** do Apêndice A.
2. Copie os arquivos de logo para `assets/img/` (lista na seção 1.2).
3. Os `.html` referenciam `assets/estilos.css` por caminho **relativo**: `assets/` fica na mesma pasta dos `.html`.
4. Carregue na ordem: Bootstrap CSS, Bootstrap Icons, `assets/estilos.css`.
5. **Não** coloque cor, fonte, raio ou sombra solta no HTML (`style="..."`). Tudo vem das variáveis `--is-*`.
6. Prefira os componentes do Bootstrap (já reestilizados). Só crie classe nova (prefixo `is-`) se não houver equivalente, e registre-a no `estilos.css`.
7. Se este texto divergir do `estilos.css`, **o CSS vence**.

---

## 1. Marca e logo

### 1.1 A logo oficial

Monitor azul com linha de crescimento e seta, seguido do nome **InoSys** em azul-marinho.
É um arquivo de imagem aprovado: **não é para recriar em SVG, redesenhar nem adicionar elementos.**

| | Cor | Hex |
|---|---|---|
| Ícone (monitor, linha e seta) | azul da logo | `#1D7DFF` |
| Nome "InoSys" | azul-marinho da logo | `#233347` |

> **Atenção:** o azul da logo (`#1D7DFF`) é cor de **identidade**. Com texto branco por cima ele dá só 3,87:1 de contraste
> (abaixo dos 4,5:1 exigidos). Por isso a interface usa um azul mais escuro para ação, o `#175CD3` (seção 3).
> Nunca use `#1D7DFF` como fundo de botão com texto, nem como cor de texto.

### 1.2 Variantes e quando usar cada uma

| Arquivo (`assets/img/`) | Aparência | Use sobre | Onde |
|---|---|---|---|
| `logo-inosys.png` | ícone azul + nome azul-marinho | fundo **claro** (branco, `#F1F3F6`) | cabeçalhos claros, documentos, e-mails |
| `logo-inosys-reversed.png` | ícone azul + nome **branco** | fundo **navy** `#0D2340` | **sidebar** e painel do login |
| `logo-inosys-mono-white.png` | tudo branco | fundo de cor sólida (ex.: azul `#175CD3`) | uso monocromático |
| `logo-inosys-icon.png` | só o monitor, azul | fundo claro, espaço pequeno | favicon, avatar, ícone de app |
| `logo-inosys-original.png` | arquivo enviado, sem corte | — | **arquivo-fonte**: não usar na interface |

Todas têm fundo **transparente**, 600 × 171 px (a do ícone, 193 × 171 px) — cerca de 2× o maior tamanho de exibição, para ficar nítida em telas de alta densidade — e proporção fixa de aproximadamente 3,5 : 1.

Pré-visualização das variantes sobre os fundos corretos:

| Fundo | Variante |
|---|---|
| branco | ![logo sobre branco](assets/img/logo-inosys.png) |
| navy `#0D2340` | usar `logo-inosys-reversed.png` |
| azul `#175CD3` | usar `logo-inosys-mono-white.png` |

### 1.3 Tamanhos e espaço livre

| Contexto | Tamanho |
|---|---|
| Sidebar | altura **33px** (largura ≈ 116px), `width: auto` |
| Painel do login | largura **150px**, `height: auto` |
| Mínimo (logo completa) | largura **96px** |
| Mínimo (só ícone) | **24px** |

- **Espaço livre mínimo** ao redor: metade da altura da logo (≈ a altura da letra "I").
- Sempre `alt="InoSys"` e `width`/`height` informados no HTML (evita salto de layout). A proporção nunca é alterada.

### 1.4 Aplicação em HTML

```html
<!-- Sidebar (fundo navy) -->
<img class="is-brand-logo" src="assets/img/logo-inosys-reversed.png" alt="InoSys" width="116" height="33">

<!-- Fundo claro -->
<img src="assets/img/logo-inosys.png" alt="InoSys" width="150" height="43">
```

### 1.5 Não fazer

- Não recolorir, aplicar sombra, contorno, degradê ou efeito.
- Não esticar nem cortar. Não girar.
- Não usar a versão colorida (`logo-inosys.png`) sobre navy: o nome em azul-marinho desaparece. Use a `reversed`.
- Não colocar sobre foto ou estampa sem uma camada sólida por trás.
- Não separar o ícone do nome, exceto com a variante `icon`.
- **Não acrescentar o ponto âmbar.** Um rascunho anterior da logo recriada em SVG tinha um ponto âmbar; ele **não existe** na logo oficial e foi removido.

---

## 2. Princípios

- **Utilitário antes de bonito.** É uma ferramenta operacional, não uma página comercial. Densidade e clareza de números vêm primeiro.
- **Cor com significado.** O azul é ação. Verde, âmbar, vermelho e azul-claro só comunicam estado. Nunca decoração.
- **Cards limpos.** Fundo branco, borda fina, cantos de 16px, sombra muito discreta, bastante espaço interno.
- **Sidebar como âncora.** Navy institucional fixo à esquerda em toda tela interna.
- **Separar design de regra de negócio.** Melhorar espaçamento, cor, hierarquia, responsividade, ícones e estados é design. Inventar campo, módulo ou fluxo não é.

---

## 3. Cores

### 3.1 Tokens (extraídos do `:root` do `estilos.css`)

| Variável | Valor | Observação |
|---|---|---|
| `--is-brand` | `#175CD3` |  |
| `--is-brand-light` | `#2F7CF6` |  |
| `--is-brand-strong` | `#0F3F8F` |  |
| `--is-amber` | `#F5A524` | destaque pontual (NÃO faz parte da logo) — só sobre fundo escuro |
| `--is-navy` | `#0D2340` |  |
| `--is-navy-2` | `#123F72` | cores da logo oficial — identidade, não usar como cor de botão/texto de UI |
| `--is-logo-blue` | `#1D7DFF` | ícone da logo (contraste com branco 3,87:1 → não serve para texto) |
| `--is-logo-ink` | `#233347` | wordmark "InoSys" sobre fundo claro |
| `--is-ink` | `#16212F` |  |
| `--is-muted` | `#62707F` |  |
| `--is-border` | `#D6DDE6` |  |
| `--is-border-soft` | `#EDF0F3` |  |
| `--is-page-bg` | `#F1F3F6` |  |
| `--is-surface` | `#FFFFFF` |  |
| `--is-success` | `#15803D` |  |
| `--is-success-tint` | `rgba(21,128,61,.10)` |  |
| `--is-warning-text` | `#92400E` | texto/ícone de atenção sobre fundo claro |
| `--is-warning-tint` | `rgba(245,165,36,.18)` |  |
| `--is-danger` | `#B42318` |  |
| `--is-danger-tint` | `rgba(180,35,24,.09)` |  |
| `--is-info-tint` | `rgba(23,92,211,.09)` |  |
| `--is-radius` | `10px` | botões, inputs |
| `--is-radius-card` | `16px` | cards, tabelas, modais |
| `--is-radius-lg` | `20px` | moldura do login |
| `--is-shadow` | `0 1px 2px rgba(22,33,47,.04), 0 4px 14px -8px rgba(22,33,47,.12)` |  |
| `--is-font` | `"IBM Plex Sans", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` |  |
| `--is-font-mono` | `"IBM Plex Mono", "SFMono-Regular", Consolas, monospace` |  |
| `--is-sidebar-w` | `240px` |  |

### 3.2 Papéis

| Papel | Token | Uso |
|---|---|---|
| Ação | `--is-brand` `#175CD3` | botão primário, links, foco, item ativo da sidebar |
| Ação (hover) | `--is-brand-strong` `#0F3F8F` | hover e pressionado do botão primário |
| Institucional | `--is-navy` `#0D2340` | sidebar e painel escuro do login (degradê para `--is-navy-2` `#123F72`) |
| Texto | `--is-ink` `#16212F` | texto principal |
| Texto secundário | `--is-muted` `#62707F` | legendas, breadcrumb, rótulos de tabela |
| Fundo da página | `--is-page-bg` `#F1F3F6` | fundo geral |
| Superfície | `--is-surface` `#FFFFFF` | cards, inputs, modais — **sempre branco** |
| Bordas | `--is-border` `#D6DDE6` · `--is-border-soft` `#EDF0F3` | contorno de card/input · divisórias internas |
| Identidade | `--is-logo-blue` `#1D7DFF` · `--is-logo-ink` `#233347` | **só** a logo (seção 1) |
| Destaque pontual | `--is-amber` `#F5A524` | detalhe sobre fundo **escuro**; moderação; não é cor principal |

### 3.3 Status — a cor só comunica estado

| Cor | Classe | Significado | Exemplos |
|---|---|---|---|
| verde | `is-badge-success` | normal / concluído / ativo | Concluída, Ativo, Normal |
| azul | `is-badge-info` | em andamento / informativo | Em andamento, Entrada, perfil Gestor |
| âmbar | `is-badge-warning` | atenção | Pendente, Estoque baixo |
| vermelho | `is-badge-danger` | problema | divergência de valor, erro |
| cinza | `is-badge-neutral` | inativo / sem dado | Desativado, Saída, perfis operacionais |
| navy | `is-badge-dark` | destaque neutro | Administrador, Anonimizado |

Padrão visual: **fundo em tinta suave + texto na cor saturada**, forma de pílula. Nunca texto branco sobre âmbar ou vermelho claro.
Os `badge text-bg-*` do Bootstrap são reestilizados no mesmo padrão como rede de segurança; em markup novo use `is-badge`.

---

## 4. Acessibilidade — contrastes verificados

| Par | Razão | Resultado |
|---|---|---|
| branco sobre `#175CD3` | 5,99:1 | ✅ texto de botão primário |
| `#15803D` sobre branco | 5,02:1 | ✅ status "sucesso" |
| `#B42318` sobre branco | 6,57:1 | ✅ status "problema" |
| `#92400E` sobre branco | 7,09:1 | ✅ texto/ícone de "atenção" sobre fundo claro |
| `#233347` (nome da logo) sobre branco | 12,84:1 | ✅ |
| `#F5A524` sobre `#0D2340` | 7,73:1 | ✅ âmbar sobre fundo escuro |
| `#1D7DFF` sobre `#0D2340` | 4,08:1 | ✅ ícone da logo sobre navy (elemento gráfico, mínimo 3:1) |
| `#1D7DFF` sobre branco / branco sobre `#1D7DFF` | 3,87:1 | ❌ **reprova para texto** |
| `#F5A524` sobre branco | 2,04:1 | ❌ **nunca** usar âmbar puro sobre fundo claro |

- Texto e ícone de "atenção" sobre fundo claro usam `--is-warning-text` `#92400E`, nunca o âmbar puro.
- Foco visível padronizado (`:focus-visible`, contorno azul). Respeita `prefers-reduced-motion`.
- A informação nunca depende só da cor: badges levam texto; alertas levam ícone.

---

## 5. Tipografia

- **IBM Plex Sans** (400, 500, 600, 700) no texto. **IBM Plex Mono** (500, 600) em **números**: quantidades, km, R$, códigos.
- Fontes carregadas do Google Fonts (já no `@import` do CSS). Fallback: `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.

| Elemento | Tamanho | Peso | Observação |
|---|---|---|---|
| Título de tela `h1.h4` | 1,5rem | 700 | `letter-spacing: -.02em` |
| Título de card | 0,95rem | 600 | |
| Texto | 0,875–1rem | 400 | |
| Rótulo de campo | 0,8125rem | 600 | |
| Cabeçalho de tabela | 0,75rem | 600 | cor secundária, sem quebra de linha |
| Número de KPI | 2rem | 600 | **Plex Mono** (`.is-metric`) |
| Valores em tabela (`td.text-end`) | 0,82rem | 400 | **Plex Mono** |
| Legenda / breadcrumb | 0,75–0,8rem | 400 | cor secundária |

---

## 6. Forma

| Elemento | Raio | Token |
|---|---|---|
| botões, inputs, badges | 10px | `--is-radius` |
| cards, tabelas, modais | 16px | `--is-radius-card` |
| moldura do login | 20px | `--is-radius-lg` |

- **Sombra:** sempre `--is-shadow` (duas camadas muito suaves). Nunca a `shadow` forte do Bootstrap.
- **Borda:** 1px `--is-border` em cards e inputs; 1px `--is-border-soft` em divisórias dentro do card.
- **Espaçamento:** escala do Bootstrap (`g-3`, `p-3`, `mb-3`, `gap-2`). Padding de card: `1.25rem`. Bastante espaço em branco.
- **Largura:** conteúdo interno em `container` de até 1180px; sidebar 240px (`--is-sidebar-w`).

---

## 7. Ícones

**Bootstrap Icons 1.11.3** (fonte via CDN). Cor herda do texto; tamanho acompanha a fonte.

| Uso | Ícone |
|---|---|
| Início | `bi-grid` |
| Estoque | `bi-box-seam` |
| Fretes / entregas | `bi-truck` |
| Visão geral | `bi-speedometer2` |
| Administração | `bi-shield-lock` |
| Usuário / senha (campos) | `bi-person`, `bi-lock` |
| Atenção / estoque baixo | `bi-exclamation-triangle` |
| Divergência de valor | `bi-cash-coin` |
| Entrada / saída | `bi-box-arrow-in-down`, `bi-box-arrow-up` |
| Histórico | `bi-clock-history` |
| Adicionar | `bi-plus-lg` |
| Desativar / reativar | `bi-pause-circle` / `bi-play-circle` |
| Anonimizar | `bi-eraser` |
| Sair / seguir | `bi-box-arrow-right` / `bi-arrow-right` |
| Menu (celular) | `bi-list` |
| Ajuda / segurança | `bi-question-circle`, `bi-shield-check` |

Ícones decorativos levam `aria-hidden="true"`. Ícone sozinho num botão precisa de `title` ou `aria-label`.

---

## 8. Bootstrap — como foi reestilizado

O Bootstrap 5.3.3 continua sendo a base. O `estilos.css` o reestiliza em **duas camadas**, então **não é preciso trocar classes no HTML**:

1. **Variáveis globais `--bs-*`** (fonte, cor do texto, fundo, primária, sucesso, perigo, atenção, links, raios). Os utilitários (`.text-primary`, `.text-danger`, `.bg-light`...) leem essas variáveis em tempo real.
2. **Variáveis locais de cada componente** (`--bs-btn-*`, `--bs-card-*`, `--bs-pagination-*`, `--bs-alert-*`...). O Bootstrap **não** herda a cor de componente a partir de `--bs-primary`, então cada componente é sobrescrito à parte.

Componentes cobertos: `btn` (primary, outline-primary, outline-secondary, outline-success, outline-danger, btn-group), `card`, `table` (hover, cabeçalho), `nav-tabs`, `modal` (e backdrop navy), `alert` (success, danger, warning), `badge` (`text-bg-*`), `pagination`, `breadcrumb`, `form-control`, `form-select`, `form-label`, `offcanvas-lg`, `spinner-border`.

Regra: **use a classe do Bootstrap**. Não recrie botão, card, tabela ou modal com CSS próprio.

---

## 9. Componentes

### 9.1 Botões
- **Primário** (`btn btn-primary`): azul `#175CD3`, texto branco, peso 600, raio 10px, sombra discreta, hover `#0F3F8F`. Uma ação principal por tela ou modal.
- **Secundário** (`btn btn-outline-secondary`): "Cancelar", "Fechar". Borda neutra, texto `--is-ink`.
- **De ação leve** (`btn btn-outline-primary`): atalhos e ações secundárias, normalmente `btn-sm`.
- **Destrutivo** (`btn-outline-danger`): Desativar, Excluir, Anonimizar. **Nunca** é a ação principal da tela; fica em linha de tabela ou dentro de modal, com confirmação.
- Sem efeitos exagerados: nada de gradiente, brilho ou animação longa.

### 9.2 Formulários
- Rótulo **acima** do campo (`form-label`), peso 600. Campo com borda `--is-border`, raio 10px.
- Foco: borda azul + anel suave (`rgba(23,92,211,.16)`).
- Campos de login levam ícone Bootstrap dentro do campo, à esquerda.
- Formulários vivem em **modal centralizado**: "Cancelar" (secundário) + ação primária no rodapé.
- Erro de validação: texto de erro abaixo do campo ou `alert-danger` no topo do modal.

### 9.3 Cards
- Fundo branco, borda 1px `--is-border`, raio 16px, `--is-shadow`, padding `1.25rem`.
- **Card de indicador (KPI):** rótulo pequeno em cinza → número grande em Plex Mono → link "Ver ..." com seta → ícone em quadrado de 38px no canto superior direito (`is-kpi-icon danger / info / warning / success`).
- **Cabeçalho de card:** título 0,95rem/600 + subtítulo cinza 0,76rem, com divisória `--is-border-soft` embaixo.

### 9.4 Tabelas
- Dentro de card, com `table-responsive`. Cabeçalho em fundo `#F7F9FB`, texto cinza 0,75rem/600, sem quebra de linha. Linhas com hover azul bem suave.
- Células numéricas alinhadas à direita e em **Plex Mono**.
- Linha em alerta (ex.: estoque baixo): marcador âmbar de 3px na borda esquerda (`tr.is-row-alert`).
- **Paginação** de 20 itens por página, abaixo da tabela, com o contador "Mostrando X de Y" à esquerda.

### 9.5 Badges de status
`is-badge is-badge-success | info | warning | danger | neutral | dark` (seção 3.3). Pílula, 0,72rem, peso 600, ícone opcional à esquerda.

### 9.6 Abas
`nav-tabs`: texto cinza, aba ativa em azul, peso 600, fundo branco, cantos superiores de 10px.

### 9.7 Modais
Centralizados, raio 16px, título 1,05rem/700, fundo escurecido em navy (opacidade 0,45).

### 9.8 Alertas
`alert-success`, `alert-danger`, `alert-warning`: fundo em tinta suave, texto na cor saturada, raio 10px, ícone à esquerda. Alerta de estoque baixo usa `alert-warning`.

### 9.9 Sidebar (telas internas)
- Largura 240px, fixa à esquerda; fundo degradê navy (170°, `#0D2340` → `#123F72`).
- Topo: **logo reversa** (33px de altura). Abaixo, rótulo de seção "MÓDULOS" (0,66rem, caixa alta, `#8FA3BA`).
- Itens: ícone + texto, altura mínima 42px, raio 9px, texto `#D2DCE8`. Hover: fundo branco a 8%. **Ativo: fundo `--is-brand`, texto branco, peso 600.**
- Rodapé: perfil (avatar circular, nome, papel) e botão "Sair" com contorno translúcido.
- Abaixo de 992px vira painel deslizante (`offcanvas-lg`), aberto por botão de menu.
- Ordem do menu: Início · Estoque · Fretes · Visão Geral · Administração. Mostra só o que o perfil pode acessar.

### 9.10 Cabeçalho de tela
Breadcrumb → título `h1.h4` → subtítulo cinza. Ações da tela à direita. Em celular, ações descem para baixo do título.

### 9.11 Gráficos
Barras e linhas em `--is-brand` (série principal) e `#A9B4C1` ou `--is-muted` tracejado (série secundária). Grade em `--is-border-soft`. Legenda em cinza, 0,75rem. Sempre com texto alternativo (`role="img"` + `aria-label`).

### 9.12 Login
Moldura única de 20px com borda e sombra discreta, dividida em dois painéis: **esquerda navy** (logo reversa, título "Gestão de estoque e monitor financeiro de fretes", mensagem institucional e chips de módulo decorativos) e **direita branca** ("Acesse sua conta", usuário e senha com ícone, botão Entrar, link de ajuda, aviso de acesso restrito). Em telas estreitas (< 820px) os painéis empilham. O CSS exclusivo do login fica no próprio `login.html`; tokens e base vêm do `estilos.css`.

---

## 10. Estados e feedback

| Estado | Padrão |
|---|---|
| Foco | contorno azul visível (`:focus-visible`), anel suave em campos |
| Hover | botão escurece para `#0F3F8F`; linha de tabela ganha tinta azul 4%; item de menu clareia |
| Desabilitado | opacidade reduzida do Bootstrap, sem cursor de ação |
| Carregando (HTMX) | `.htmx-indicator` (spinner) aparece; o alvo esmaece (`.htmx-request`, opacidade .55) |
| Troca de conteúdo | `.htmx-swapping` apaga em 120 ms; `.htmx-settling` reaparece em 120 ms |
| Erro dentro de modal | `.is-swap-error`: some quando vazio, aparece como `alert-danger` quando recebe texto |
| Mensagem de sucesso/erro | aviso (`alert`) flutuante no canto inferior direito, some em 4 s |
| Vazio | texto cinza curto dizendo o que fazer; sem ilustração |
| Movimento | transições curtas (≤ 200 ms); `prefers-reduced-motion` desliga todas |

---

## 11. Responsividade

| Largura | Comportamento |
|---|---|
| ≥ 992px | sidebar fixa; conteúdo com margem de 240px |
| < 992px | sidebar vira painel deslizante; botão de menu aparece no cabeçalho |
| < 820px | login empilha os dois painéis |
| celular | tabelas com rolagem horizontal; ações do cabeçalho descem; botões ocupam a largura quando necessário |

Testar sempre em largura de celular (F12 → Ctrl+Shift+M).

---

## 12. Checklist para tela nova

- [ ] Só variáveis `--is-*` e componentes do Bootstrap; nenhum `style="..."` com cor, fonte ou raio.
- [ ] Logo na variante certa para o fundo (`reversed` no navy, `logo-inosys.png` no claro).
- [ ] Cards: branco, borda fina, 16px, sombra discreta, espaço interno.
- [ ] Números em Plex Mono; status em `is-badge-*` seguindo o mapa de cores.
- [ ] Atenção sobre fundo claro com `#92400E`, nunca âmbar puro.
- [ ] Uma ação principal azul por tela; destrutivo nunca é o principal.
- [ ] Foco visível e `alt`/`aria-label` nos ícones e imagens.
- [ ] Testada em largura de celular.
- [ ] Nenhum campo, módulo ou fluxo inventado.

---

## Apêndice A — `assets/estilos.css` (completo)

```css
/* ============================================================
   INOSYS — assets/estilos.css
   Folha de estilo ÚNICA do sistema. Todas as telas linkam este
   arquivo; cada .html só guarda no próprio <style> o que for
   exclusivo dela (hoje, apenas o login).

   1. Fontes e tokens
   2. Reskin das variáveis nativas do Bootstrap 5.3
      (faz btn, card, table, badge, tabs e modal do Bootstrap
      já saírem na identidade InoSys, sem trocar classes no HTML)
   3. Sidebar institucional (injetada por assets/sidebar.js)
   4. Layout das telas internas
   5. Componentes de dashboard (KPI, gráfico, relatórios)
   6. Badges de status
   7. Estados do HTMX (carregando)
   ============================================================ */

@import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap");

/* ---------- 1. Tokens ---------- */
:root {
  --is-brand: #175CD3;
  --is-brand-light: #2F7CF6;
  --is-brand-strong: #0F3F8F;
  --is-amber: #F5A524;          /* destaque pontual (NÃO faz parte da logo) — só sobre fundo escuro */
  --is-navy: #0D2340;
  --is-navy-2: #123F72;

  /* cores da logo oficial — identidade, não usar como cor de botão/texto de UI */
  --is-logo-blue: #1D7DFF;      /* ícone da logo (contraste com branco 3,87:1 → não serve para texto) */
  --is-logo-ink: #233347;       /* wordmark "InoSys" sobre fundo claro */

  --is-ink: #16212F;
  --is-muted: #62707F;
  --is-border: #D6DDE6;
  --is-border-soft: #EDF0F3;
  --is-page-bg: #F1F3F6;
  --is-surface: #FFFFFF;

  /* status: verde=normal, âmbar=atenção, vermelho=problema, azul=andamento */
  --is-success: #15803D;
  --is-success-tint: rgba(21,128,61,.10);
  --is-warning-text: #92400E;   /* texto/ícone de atenção sobre fundo claro */
  --is-warning-tint: rgba(245,165,36,.18);
  --is-danger: #B42318;
  --is-danger-tint: rgba(180,35,24,.09);
  --is-info-tint: rgba(23,92,211,.09);

  --is-radius: 10px;       /* botões, inputs */
  --is-radius-card: 16px;  /* cards, tabelas, modais */
  --is-radius-lg: 20px;    /* moldura do login */
  --is-shadow: 0 1px 2px rgba(22,33,47,.04), 0 4px 14px -8px rgba(22,33,47,.12);

  --is-font: "IBM Plex Sans", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --is-font-mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
  --is-sidebar-w: 240px;
}

/* ---------- 2. Reskin do Bootstrap ---------- */
:root {
  --bs-font-sans-serif: var(--is-font);
  --bs-body-font-family: var(--is-font);
  --bs-body-color: var(--is-ink);
  --bs-body-bg: var(--is-page-bg);
  --bs-secondary-color: var(--is-muted);
  --bs-border-color: var(--is-border);
  --bs-border-radius: var(--is-radius);
  --bs-border-radius-sm: 8px;
  --bs-border-radius-lg: var(--is-radius-card);
  --bs-primary: var(--is-brand);
  --bs-primary-rgb: 23, 92, 211;
  --bs-success: var(--is-success);
  --bs-success-rgb: 21, 128, 61;
  --bs-danger: var(--is-danger);
  --bs-danger-rgb: 180, 35, 24;
  --bs-warning: var(--is-warning-text);
  --bs-warning-rgb: 146, 64, 14;
  --bs-light-rgb: 241, 243, 246;       /* .bg-light passa a ser o fundo da marca */
  --bs-link-color: var(--is-brand);
  --bs-link-color-rgb: 23, 92, 211;
  --bs-link-hover-color: var(--is-brand-strong);
  --bs-link-hover-color-rgb: 15, 63, 143;
  --bs-focus-ring-color: rgba(23, 92, 211, .25);
}

body { font-family: var(--is-font); color: var(--is-ink); background: var(--is-page-bg); }
.text-muted { color: var(--is-muted) !important; }

/* Botões */
.btn { border-radius: var(--is-radius); font-weight: 600; }
.btn-primary {
  --bs-btn-bg: var(--is-brand); --bs-btn-border-color: var(--is-brand);
  --bs-btn-hover-bg: var(--is-brand-strong); --bs-btn-hover-border-color: var(--is-brand-strong);
  --bs-btn-active-bg: var(--is-brand-strong); --bs-btn-active-border-color: var(--is-brand-strong);
  --bs-btn-disabled-bg: var(--is-brand); --bs-btn-disabled-border-color: var(--is-brand);
  --bs-btn-focus-shadow-rgb: 23, 92, 211;
  box-shadow: 0 1px 2px rgba(15,63,143,.2);
}
.btn-outline-primary {
  --bs-btn-color: var(--is-brand); --bs-btn-border-color: var(--is-brand);
  --bs-btn-hover-bg: var(--is-brand); --bs-btn-hover-border-color: var(--is-brand);
  --bs-btn-active-bg: var(--is-brand); --bs-btn-active-border-color: var(--is-brand);
  --bs-btn-disabled-color: var(--is-brand); --bs-btn-disabled-border-color: var(--is-brand);
  --bs-btn-focus-shadow-rgb: 23, 92, 211;
}
.btn-outline-secondary {
  --bs-btn-color: var(--is-ink); --bs-btn-border-color: var(--is-border);
  --bs-btn-hover-bg: var(--is-page-bg); --bs-btn-hover-color: var(--is-ink); --bs-btn-hover-border-color: #B9C3CF;
  --bs-btn-active-bg: var(--is-page-bg); --bs-btn-active-color: var(--is-ink); --bs-btn-active-border-color: #B9C3CF;
}
.btn-outline-success {
  --bs-btn-color: var(--is-success); --bs-btn-border-color: var(--is-success);
  --bs-btn-hover-bg: var(--is-success); --bs-btn-hover-border-color: var(--is-success);
}
.btn-outline-danger {
  --bs-btn-color: var(--is-danger); --bs-btn-border-color: var(--is-danger);
  --bs-btn-hover-bg: var(--is-danger); --bs-btn-hover-border-color: var(--is-danger);
}
.btn-group > .btn { border-radius: var(--is-radius); }
.btn-group > .btn:not(:last-child) { border-top-right-radius: 0; border-bottom-right-radius: 0; }
.btn-group > .btn:not(:first-child) { border-top-left-radius: 0; border-bottom-left-radius: 0; }

/* Formulários */
.form-control, .form-select { border-color: var(--is-border); border-radius: var(--is-radius); }
.form-control:focus, .form-select:focus {
  border-color: var(--is-brand);
  box-shadow: 0 0 0 .2rem rgba(23,92,211,.16);
}
.form-label { font-size: .8125rem; font-weight: 600; color: var(--is-ink); }

/* Cards: borda fina, cantos 16px, sombra muito discreta */
.card {
  --bs-card-border-color: var(--is-border);
  --bs-card-border-radius: var(--is-radius-card);
  --bs-card-inner-border-radius: calc(var(--is-radius-card) - 1px);
  --bs-card-spacer-y: 1.25rem;
  --bs-card-spacer-x: 1.25rem;
}
.card, .card.shadow-sm, .shadow-sm { box-shadow: var(--is-shadow) !important; }

/* Tabelas */
.table {
  --bs-table-color: var(--is-ink);
  --bs-table-hover-bg: rgba(23,92,211,.04);
  --bs-table-border-color: var(--is-border-soft);
  margin-bottom: 0;
}
.table > thead th,
.table-light > tr > th,
.table > .table-light th {
  --bs-table-bg: #F7F9FB;
  color: var(--is-muted);
  font-size: .75rem;
  font-weight: 600;
  letter-spacing: .02em;
  border-bottom-color: var(--is-border);
  white-space: nowrap;
}
.table td { font-size: .875rem; }
.table td.text-end { font-family: var(--is-font-mono); font-size: .82rem; } /* km, R$, quantidades */

/* Abas */
.nav-tabs { --bs-nav-tabs-border-color: var(--is-border); }
.nav-tabs .nav-link {
  color: var(--is-muted);
  font-size: .875rem;
  font-weight: 500;
  border-radius: var(--is-radius) var(--is-radius) 0 0;
}
.nav-tabs .nav-link:hover { color: var(--is-ink); border-color: transparent; }
.nav-tabs .nav-link.active {
  color: var(--is-brand);
  font-weight: 600;
  background: var(--is-surface);
  border-color: var(--is-border) var(--is-border) var(--is-surface);
}

/* Modais */
.modal { --bs-modal-border-radius: var(--is-radius-card); --bs-modal-inner-border-radius: calc(var(--is-radius-card) - 1px); --bs-modal-border-color: var(--is-border); }
.modal-title { font-size: 1.05rem; font-weight: 700; }
.modal-backdrop { --bs-backdrop-bg: #0D2340; --bs-backdrop-opacity: .45; }

/* Alertas */
.alert { border-radius: var(--is-radius); font-size: .875rem; }
.alert-success { --bs-alert-bg: var(--is-success-tint); --bs-alert-color: var(--is-success); --bs-alert-border-color: rgba(21,128,61,.2); }
.alert-danger  { --bs-alert-bg: var(--is-danger-tint);  --bs-alert-color: var(--is-danger);  --bs-alert-border-color: rgba(180,35,24,.2); }
.alert-warning { --bs-alert-bg: var(--is-warning-tint); --bs-alert-color: var(--is-warning-text); --bs-alert-border-color: rgba(245,165,36,.35); }

/* Badges do Bootstrap já usados nos mockups (text-bg-*) → tinta suave + texto forte */
.badge { font-weight: 600; font-size: .72rem; padding: .35em .65em; }
.badge.text-bg-success   { background: var(--is-success-tint) !important; color: var(--is-success) !important; }
.badge.text-bg-warning   { background: var(--is-warning-tint) !important; color: var(--is-warning-text) !important; }
.badge.text-bg-danger    { background: var(--is-danger-tint) !important;  color: var(--is-danger) !important; }
.badge.text-bg-info      { background: var(--is-info-tint) !important;    color: var(--is-brand) !important; }
.badge.text-bg-primary   { background: var(--is-info-tint) !important;    color: var(--is-brand) !important; }
.badge.text-bg-secondary { background: #EEF1F4 !important; color: var(--is-muted) !important; }
.badge.text-bg-light     { background: transparent !important; color: #A3ADB8 !important; }

.breadcrumb { font-size: .8rem; --bs-breadcrumb-divider-color: #A3ADB8; --bs-breadcrumb-item-active-color: var(--is-muted); }
.breadcrumb a { text-decoration: none; }

/* Números tabulares */
.is-metric { font-family: var(--is-font-mono); font-weight: 600; letter-spacing: -.02em; }

/* ---------- 3. Sidebar institucional ----------
   Marcação gerada por assets/sidebar.js dentro de #sidebar-root.
   Usa .offcanvas-lg do Bootstrap: fixa em telas ≥992px e painel
   deslizante abaixo disso (abre pelo botão hambúrguer das telas). */
.is-sidebar {
  --bs-offcanvas-width: var(--is-sidebar-w);
  background-color: var(--is-navy) !important;
  background-image: linear-gradient(170deg, var(--is-navy) 0%, var(--is-navy-2) 140%) !important;
  color: #fff;
}
.is-sidebar .offcanvas-header { padding: 16px 16px 0; }
.is-sidebar .btn-close { filter: invert(1) grayscale(1) brightness(2); }
.is-sidebar .offcanvas-body {
  display: flex !important;
  flex-direction: column;
  flex-grow: 1 !important;
  padding: 22px 14px 16px !important;
  overflow-y: auto !important;
}
@media (min-width: 992px) {
  .is-sidebar.offcanvas-lg {
    position: fixed; top: 0; bottom: 0; left: 0;
    width: var(--is-sidebar-w);
    display: flex; flex-direction: column;
    z-index: 1030;
  }
  .conteudo { margin-left: var(--is-sidebar-w); }
}

/* Logo oficial na sidebar (versão reversa, assets/img/logo-inosys-reversed.png) */
.is-brand { display: flex; align-items: center; padding: 2px 10px 24px; }
.is-brand-logo { display: block; height: 33px; width: auto; }

.is-section-label { padding: 0 10px 8px; color: #8FA3BA; font-size: .66rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }

.is-nav { list-style: none; margin: 0; padding: 0; }
.is-nav-link {
  display: flex; align-items: center; gap: 10px;
  min-height: 42px; padding: 9px 11px; margin-bottom: 3px;
  border-radius: 9px;
  color: #D2DCE8; text-decoration: none; font-size: .875rem;
  transition: background .15s ease, color .15s ease;
}
.is-nav-link i { width: 19px; text-align: center; font-size: 1rem; }
.is-nav-link:hover { color: #fff; background: rgba(255,255,255,.08); }
.is-nav-link.active { color: #fff; background: var(--is-brand); font-weight: 600; }

.is-sidebar-bottom { margin-top: auto; padding-top: 16px; }
.is-profile-select {
  width: 100%; border: 1px solid rgba(255,255,255,.3); border-radius: 8px;
  padding: 7px 10px; background: rgba(255,255,255,.04); color: #fff; font-size: .78rem;
}
.is-profile-select option { color: var(--is-ink); }
.is-profile { display: flex; align-items: center; gap: 10px; margin-top: 14px; padding: 14px 6px 6px; border-top: 1px solid rgba(255,255,255,.14); }
.is-profile-avatar { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff; }
.is-profile-name { color: #fff; font-size: .82rem; font-weight: 600; line-height: 1.2; }
.is-profile-role { color: #9FB0C4; font-size: .7rem; }
.is-logout {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: 100%; margin-top: 10px; padding: 7px 10px;
  border: 1px solid rgba(255,255,255,.3); border-radius: 8px;
  color: #fff; font-size: .78rem; text-decoration: none;
}
.is-logout:hover { background: rgba(255,255,255,.08); color: #fff; }

/* ---------- 4. Layout das telas internas ---------- */
.conteudo { min-height: 100vh; }
.conteudo > .container,
.conteudo > .container-fluid { max-width: 1180px; padding-top: 28px !important; padding-bottom: 40px !important; }
.conteudo h1.h4 { font-weight: 700; letter-spacing: -.02em; }

/* ---------- 5. Componentes de dashboard ---------- */
.is-kpi { position: relative; padding: 18px 18px 14px; height: 100%; }
.is-kpi-label { color: var(--is-muted); font-size: .78rem; padding-right: 44px; }
.is-kpi-value { margin: 6px 0 0; font-size: 2rem; line-height: 1; }
.is-kpi-link { display: inline-flex; gap: 4px; margin-top: 12px; font-size: .78rem; font-weight: 500; text-decoration: none; }
.is-kpi-link:hover { text-decoration: underline; }
.is-kpi-icon { position: absolute; top: 16px; right: 16px; width: 38px; height: 38px; display: grid; place-items: center; border-radius: 10px; font-size: 1.1rem; }
.is-kpi-icon.danger  { background: var(--is-danger-tint);  color: var(--is-danger); }
.is-kpi-icon.info    { background: var(--is-info-tint);    color: var(--is-brand); }
.is-kpi-icon.warning { background: var(--is-warning-tint); color: var(--is-warning-text); }
.is-kpi-icon.success { background: var(--is-success-tint); color: var(--is-success); }

.is-card-header { padding-bottom: 10px; margin-bottom: 12px; border-bottom: 1px solid var(--is-border-soft); }
.is-card-title { margin: 0; font-size: .95rem; font-weight: 600; }
.is-card-subtitle { margin-top: 2px; color: var(--is-muted); font-size: .76rem; }

.is-chart-bars { display: flex; align-items: flex-end; gap: 1.25rem; height: 170px; padding: 0 4px; border-bottom: 1px solid var(--is-border); }
.is-chart-bars .grupo { display: flex; align-items: flex-end; gap: 4px; flex: 1 1 0; height: 100%; }
.is-chart-bars .barra { flex: 1 1 0; background: var(--is-brand); border-radius: 4px 4px 0 0; min-height: 4px; }
.is-chart-bars .barra.saida { background: #A9B4C1; }
.is-legend { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 10px; font-size: .75rem; color: var(--is-muted); }
.is-legend span { display: inline-flex; align-items: center; gap: 6px; }
.is-legend .swatch { width: 10px; height: 10px; border-radius: 3px; background: var(--is-brand); }
.is-legend .swatch.muted { background: #A9B4C1; }
.is-legend .line { width: 16px; border-top: 2px solid var(--is-brand); }
.is-legend .line.dashed { border-top: 2px dashed var(--is-muted); }

/* Aviso de estoque baixo dentro de tabela */

/* ---------- 6. Badges de status (para markup novo) ---------- */
.is-badge { display: inline-flex; align-items: center; gap: .3rem; padding: .22rem .6rem; border-radius: 999px; font-size: .72rem; font-weight: 600; }
.is-badge-success { background: var(--is-success-tint); color: var(--is-success); }
.is-badge-warning { background: var(--is-warning-tint); color: var(--is-warning-text); }
.is-badge-danger  { background: var(--is-danger-tint);  color: var(--is-danger); }
.is-badge-info    { background: var(--is-info-tint);    color: var(--is-brand); }
.is-badge-neutral { background: #EEF1F4; color: var(--is-muted); }

/* ---------- 7. Estados do HTMX ----------
   htmx adiciona .htmx-request ao elemento enquanto a requisição
   está em andamento — aqui viram feedback visual padronizado. */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator, .htmx-request.htmx-indicator { display: inline-block; }
[hx-target].htmx-request, .is-swap-target.htmx-request { opacity: .55; transition: opacity .15s; }
.htmx-swapping { opacity: 0; transition: opacity .12s ease-out; }
.htmx-settling { opacity: 1; transition: opacity .12s ease-in; }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}

/* ============================================================
   8. Complementos do design system (aplicados às telas antigas)
   ============================================================ */

/* Badge escuro (perfil Administrador, dados anonimizados) e badge de perfil (não é status) */
.is-badge-dark { background: rgba(13,35,64,.10); color: var(--is-navy); }
.badge.text-bg-dark { background: rgba(13,35,64,.10) !important; color: var(--is-navy) !important; }

/* Paginação (20 itens/página — Paginator do Django) */
.pagination {
  --bs-pagination-color: var(--is-ink);
  --bs-pagination-border-color: var(--is-border);
  --bs-pagination-hover-bg: var(--is-page-bg);
  --bs-pagination-hover-color: var(--is-ink);
  --bs-pagination-hover-border-color: #B9C3CF;
  --bs-pagination-focus-color: var(--is-brand);
  --bs-pagination-focus-box-shadow: 0 0 0 .2rem rgba(23,92,211,.16);
  --bs-pagination-active-bg: var(--is-brand);
  --bs-pagination-active-border-color: var(--is-brand);
  --bs-pagination-disabled-color: #A3ADB8;
  --bs-pagination-border-radius: var(--is-radius);
}

/* Cards de módulo da tela de seleção */
.module-card { border-radius: var(--is-radius-card); color: var(--is-ink); transition: border-color .15s, transform .15s, box-shadow .15s; }
.module-card:hover { border-color: var(--is-brand); transform: translateY(-2px); box-shadow: 0 8px 20px -10px rgba(23,92,211,.35) !important; color: var(--is-ink); }
.module-card .bi { color: var(--is-brand) !important; }
.module-card:focus-visible { outline: 3px solid rgba(23,92,211,.35); outline-offset: 2px; }

/* Botões de "simular perfil" — estado ativo em azul da marca */
.btn-perfil.active, .btn-perfil.active:hover {
  background: var(--is-info-tint); color: var(--is-brand);
  border-color: var(--is-brand); font-weight: 600;
}

/* Senha temporária (exibida uma única vez) */
code { color: var(--is-navy); background: var(--is-page-bg); border: 1px dashed var(--is-border); border-radius: 8px; padding: .15rem .5rem; font-family: var(--is-font-mono); }

/* Foco visível padronizado (acessibilidade) */
:focus-visible { outline-color: var(--is-brand); }

/* ============================================================
   9. Modo de desenvolvimento do HTMX  (abra qualquer tela com ?htmx=1)
   Destaca todos os elementos com hx-* e lista os pontos de troca
   de conteúdo no painel flutuante montado por assets/sidebar.js.
   ============================================================ */
.htmx-debug [hx-get], .htmx-debug [hx-post], .htmx-debug [hx-put], .htmx-debug [hx-delete] {
  outline: 2px dashed var(--is-amber); outline-offset: 3px;
}
.htmx-debug [hx-target], .htmx-debug .is-swap-target { position: relative; }
.is-htmx-panel {
  position: fixed; left: 16px; bottom: 16px; z-index: 1100; width: min(420px, calc(100vw - 32px));
  max-height: 55vh; overflow: auto; padding: 14px 16px;
  background: var(--is-navy); color: #fff; border-radius: var(--is-radius-card);
  box-shadow: 0 12px 32px rgba(13,35,64,.35); font-size: .78rem;
}
.is-htmx-panel h2 { margin: 0 0 8px; font-size: .85rem; font-weight: 700; }
.is-htmx-panel .hook { display: block; width: 100%; text-align: left; margin-top: 6px; padding: 8px 10px; border: 1px solid rgba(255,255,255,.14); border-radius: 8px; background: rgba(255,255,255,.05); color: #fff; }
.is-htmx-panel .hook:hover { background: rgba(255,255,255,.12); }
.is-htmx-panel .verbo { display: inline-block; min-width: 42px; margin-right: 6px; padding: 1px 6px; border-radius: 6px; background: var(--is-amber); color: var(--is-navy); font-family: var(--is-font-mono); font-weight: 600; font-size: .7rem; text-align: center; }
.is-htmx-panel .url { font-family: var(--is-font-mono); font-size: .74rem; }
.is-htmx-panel .meta { display: block; margin-top: 3px; color: #9FB0C4; }

/* Aviso de erro devolvido pelo servidor dentro de um modal: some quando está vazio */
.is-swap-error:empty { display: none; }
/* Linha de estoque baixo: marcador âmbar (atenção) */
tr.is-row-alert td:first-child { box-shadow: inset 3px 0 0 var(--is-amber); }

/* ============================================================
   10. Compatibilidade com as telas ORIGINAIS do time
   O visao-geral.html antigo usa estas classes (que existiam no
   estilos.css original, nunca versionado). Mantidas para a tela
   antiga já sair no design system, sem editar o HTML.
   Em telas novas, prefira .is-chart-bars e .is-legend.
   ============================================================ */
.chart-barras { display: flex; align-items: flex-end; gap: 1.25rem; height: 170px; padding: 0 4px; border-bottom: 1px solid var(--is-border); }
.grupo-barras { display: flex; align-items: flex-end; gap: 4px; flex: 1 1 0; height: 100%; }
.chart-barras .barra { flex: 1 1 0; background: var(--is-brand); border-radius: 4px 4px 0 0; min-height: 4px; }
.chart-barras .barra-saida { background: #A9B4C1; }
.item-legenda { display: inline-flex; align-items: center; gap: 6px; font-size: .75rem; color: var(--is-muted); }
.quadrado-legenda { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }

/* Cores soltas do Bootstrap padrão que ficaram no HTML antigo → tokens da marca */
.quadrado-legenda[style*="0d6efd"] { background-color: var(--is-brand) !important; }
.quadrado-legenda[style*="6c757d"] { background-color: #A9B4C1 !important; }
svg polyline[stroke="#0d6efd"] { stroke: var(--is-brand); }
svg polyline[stroke="#6c757d"] { stroke: var(--is-muted); }
svg g[stroke="#dee2e6"] { stroke: var(--is-border-soft); }
.bi.text-primary { color: var(--is-brand) !important; }
```

## Apêndice B — Arquivos da logo (`assets/img/`)

| Arquivo | Dimensão | Uso |
|---|---|---|
| `logo-inosys.png` | 600 × 171 px | fundo claro: cabeçalhos, documentos, e-mails |
| `logo-inosys-reversed.png` | 600 × 171 px | fundo navy: sidebar e painel do login |
| `logo-inosys-mono-white.png` | 600 × 171 px | fundo de cor sólida, uso monocromático |
| `logo-inosys-icon.png` | 193 × 171 px | favicon, avatar, espaço pequeno |
| `logo-inosys-original.png` | 1536 × 1024 px | arquivo-fonte enviado (não usar na interface) |
