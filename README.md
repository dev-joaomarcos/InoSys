# InoSys

Gestor de estoque e monitor financeiro de fretes para a INOVE Divisórias e Forros.

Sistema web dividido em dois módulos: controle de estoque com atualização automática de saldo e alertas de reposição, e monitoramento de fretes com cálculo automático de valor sugerido por quilômetro. Desenvolvido como Projeto Integrado Multidisciplinar do curso de Análise e Desenvolvimento de Sistemas.

Este README serve como guia de referência rápida do projeto.

---

## Stack

| Item | Versão |
|---|---|
| Python | 3.14.6 |
| Django | 6.1.1 |
| PostgreSQL | 18 |
| psycopg (driver) | 3.3.5 |
| python-decouple (opcional) | 3.8 |
| Frontend | HTML + HTMX + Bootstrap 5 ou DaisyUI (tailwind) |

## Estrutura de apps

| App | Responsabilidade | Complexidade |
|---|---|---|
| `auth` | Autenticação, perfis de usuário, permissões e log de ações | Alta |
| `estoque` | Materiais, entradas, saídas, alertas e histórico | Média |
| `fretes` | Entregadores, entregas, cálculo de valor sugerido e histórico | Média |
| `relatorios` | Dashboard de visão geral, relatórios e integração entre módulos | Baixa |

O app `relatorios` é o único que importa dados dos demais. Os outros são independentes entre si.

---

## Perfis de usuário

- **Operacional de Estoque** — acessa apenas o módulo de estoque
- **Operacional de Fretes** — acessa apenas o módulo de fretes
- **Gestor** — acessa os dois módulos + dashboard de visão geral + relatórios
- **Administrador** — acesso completo, incluindo gestão de usuários, log de ações e anonimização de dados

Cadastro de usuário é feito exclusivamente pelo Administrador, que gera uma senha temporária exibida uma única vez em tela. Não há autocadastro nem envio de credenciais por e-mail. No primeiro login, a troca de senha é obrigatória. Recuperação de senha esquecida segue o mesmo fluxo: o Administrador gera uma nova senha temporária.

---

## Checklist de entregas

### Fase 1 — Base do sistema
*Dependência: nenhuma. Obrigatória antes de tudo.*

- [ ] Projeto Django configurado, `venv` documentado no README/guia de setup
- [ ] Configuração do banco via `.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- [ ] `tb_usuarios` criada e migrada
- [ ] RF01 — Login com redirecionamento por perfil
- [ ] RNF04 — Senha armazenada com hash (padrão Django)
- [ ] RNF05 — Decorators/middleware de controle de acesso por perfil
- [ ] Fluxo de senha temporária + troca obrigatória no primeiro login
- [ ] Botão "Solicitar ajuda aos administradores" (substitui recuperação por e-mail)
- [ ] Documentar como criar o Administrador inicial (`createsuperuser`)

**Entregável:** qualquer usuário autentica e é redirecionado ao dashboard correto.

### Fase 2 — Estoque e Fretes (paralelo)
*Dependência: Fase 1 concluída.*

**Estoque**
- [ ] `tb_materiais` criada e migrada (com `qtd_atual`)
- [ ] RF02 — CRUD de materiais
- [ ] RF03 — Registro de entradas (atualiza `qtd_atual` automaticamente)
- [ ] RF04 — Registro de saídas (valida saldo, atualiza `qtd_atual`)
- [ ] RF05 — Alerta de estoque baixo (checagem simples ao carregar a tela)
- [ ] `tb_movimentacoes` criada e migrada

**Fretes**
- [ ] `tb_entregadores` criada e migrada
- [ ] RF07 — CRUD de entregadores
- [ ] RF08 — Registro de entregas com cálculo automático de valor sugerido
- [ ] RF09 — Edição de entregas (independente do status)
- [ ] RF10 — Status de entregas (pendente/em andamento/concluída)
- [ ] `tb_entregas` criada e migrada

**Entregável:** usuário operacional registra movimentações e entregas completas.

### Fase 3 — Histórico e relatórios
*Dependência: Fase 2 concluída.*

- [ ] RF06 — Histórico de movimentações com filtros (material, tipo, período)
- [ ] RF11 — Histórico de entregas com filtros (entregador, status, período)
- [ ] Paginação com `Paginator` nativo do Django (20 itens/página) nas duas listas acima
- [ ] RF12 — Relatório de movimentações (somente em tela, sem exportação por ora)
- [ ] RF12 — Relatório de fretes com destaque de divergência (valor sugerido x cobrado)
- [ ] RNF01 — Consultas/relatórios respondendo em até 5s

**Entregável:** gestor consulta históricos paginados e relatórios filtrados.

### Fase 4 — Administração e finalização
*Dependência: Fase 3 concluída.*

- [ ] RF13 — CRUD de usuários pelo Administrador (com geração de senha temporária)
- [ ] RF14 — Log de ações — registro manual dentro das views (sem lib de auditoria automática)
- [ ] `tb_log_acoes` criada e migrada (com snapshot do nome do usuário)
- [ ] Paginação também no log de ações
- [ ] RF15 — Anonimização de dados pessoais — substituição por valores fixos genéricos
- [ ] RNF02 — Integridade referencial (bloqueio de exclusão de material/entregador com histórico vinculado)
- [ ] RNF10 — Rotina de backup do banco (mínimo diário)

**Entregável:** sistema funcional completo, cobrindo todo o escopo do MVP.

### Transversais (validar continuamente)

- [ ] RNF03 — Usabilidade (interface simples, poucos cliques)
- [ ] RNF06 — Responsividade (Bootstrap padrão, evitar CSS customizado excessivo)
- [ ] RNF07 — Separação clara entre models, views e templates
- [ ] RNF08 — Disponibilidade (depende da plataforma escolhida no deploy)
- [ ] RNF09 — Escalabilidade moderada
- [ ] RNF11 — Suporte a 5 usuários simultâneos

---

## Modelo de dados

> Campos confirmados pelo texto do relatório original estão sem marcação especial. Os destacados em **negrito** foram decisões tomadas durante o planejamento deste guia.

### tb_usuarios
| Campo | Observação |
|---|---|
| id (PK) | |
| nome | |
| username | único |
| senha_hash | RNF04 |
| perfil | Operacional Estoque / Operacional Fretes / Gestor / Administrador |
| status | ativo/inativo — exclusão lógica |
| senha_temporaria | booleano — controla obrigatoriedade de troca no 1º login |
| data_criacao | |

### tb_materiais
| Campo | Observação |
|---|---|
| id (PK) | |
| nome | obrigatório |
| descricao | |
| unidade_medida | obrigatório |
| quantidade_minima | obrigatório, aciona alerta (RF05) |
| **qtd_atual** | evita somar histórico a cada leitura |
| status | ativo/inativo |

### tb_movimentacoes
| Campo | Observação |
|---|---|
| id (PK) | |
| material_id (FK) | → tb_materiais |
| usuario_id (FK) | → tb_usuarios, responsável pelo registro |
| tipo | entrada / saída |
| quantidade | |
| data | |
| motivo | só para saída: uso em produção, perda ou dano, ajuste de inventário |

### tb_entregadores
| Campo | Observação |
|---|---|
| id (PK) | |
| nome | obrigatório |
| contato | |
| valor_por_km | obrigatório |
| status | ativo/inativo |

### tb_entregas
| Campo | Observação |
|---|---|
| id (PK) | |
| entregador_id (FK) | → tb_entregadores |
| usuario_id (FK) | → tb_usuarios, responsável pelo registro |
| destino | obrigatório |
| data | obrigatório |
| distancia | obrigatório |
| valor_sugerido | calculado automaticamente |
| valor_cobrado | manual ou aceito do sugerido |
| status | pendente / em andamento / concluída |

### tb_log_acoes
| Campo | Observação |
|---|---|
| id (PK) | |
| usuario_id (FK) | → tb_usuarios |
| usuario_nome_snapshot | preserva nome mesmo após exclusão do usuário |
| acao | criação / edição / exclusão |
| data_hora | |

---

## Decisões de simplicidade

| Tema | Decisão | Por quê |
|---|---|---|
| Saldo do estoque | Campo `qtd_atual` armazenado | Evita somar histórico a cada leitura de tela |
| Cadastro de usuário | Admin gera senha temporária manualmente | Volume pequeno de usuários, sem infra de e-mail |
| Recuperação de senha | Admin gera nova senha temporária | Reaproveita o mesmo fluxo do cadastro |
| Log de ações | Registro manual nas views | Mais simples e explícito que lib de auditoria automática |
| Anonimização (LGPD) | Substituição por valores fixos genéricos | Suficiente para o escopo do RF15 |
| Comprovantes de entrega (fotos) | Fora do escopo | Não fazia parte do MVP definido |
| Exportação de relatórios | Somente em tela por ora | Evita libs extras; revisar se for exigido depois |
| Paginação | `Paginator` nativo do Django, 20 itens/página | Nativo do framework, sem dependência externa |
| Ambientes | Dev local + 1 ambiente de apresentação do MVP | Sem staging separado por ora |
| Banco de dados | PostgreSQL 18 local via venv | Docker fica como esqueleto para ativação futura |
| Driver do banco | psycopg 3 (`psycopg[binary]`) | Versão atual recomendada pelo próprio PostgreSQL |

---

## Pendências em aberto

- [ ] Confirmar se o diagrama original do modelo lógico (relatório do PIM) define tipos de dado, tamanhos de campo ou constraints além dos listados aqui
- [ ] Definir biblioteca de gráficos para o dashboard de visão geral (provavelmente chart.js)
