# App `contas`

Autenticação, perfis, administração de usuários e log de ações. Também guarda o que os outros apps compartilham.

Requisitos cobertos: RF01, RF13, RF14, RF15, RNF04, RNF05.

## Models

### `Usuario` (substitui o usuário padrão do Django)

| Campo | Observação |
| --- | --- |
| `username` | Único. É o identificador de login |
| `nome` | Nome de exibição |
| `password` | Hash padrão do Django |
| `perfil` | `estoque`, `fretes`, `gestor` ou `admin` (`PerfilUsuario`) |
| `ativo` | Exclusão lógica. `is_active` devolve este campo, então inativo não entra |
| `senha_temporaria` | `True` obriga a troca de senha no próximo acesso |
| `anonimizado` | `True` após a anonimização; o registro fica bloqueado para edição |
| `data_criacao` | Automático |

Propriedades: `nome_exibicao`, `iniciais`, `pode_estoque`, `pode_fretes`, `pode_visao`, `pode_admin`. `is_staff` é verdadeiro para superusuário ou perfil `admin`.

`createsuperuser` sempre cria com perfil `admin`.

### `LogAcao`

| Campo | Observação |
| --- | --- |
| `usuario` | FK opcional (`SET_NULL`) |
| `usuario_nome_snapshot` | Cópia do nome na hora da ação |
| `acao` | `criacao`, `edicao` ou `exclusao` |
| `data_hora` | Automático |

O log registra quem, o tipo de ação e quando. Ele não registra qual registro foi alterado (ver [pendências](../pendencias.md)).

## Fluxos

### Apresentação (landing page)

- `/` sem login mostra a apresentação pública do sistema (`ApresentacaoView`, template `contas/apresentacao.html`). Com login, `/` continua sendo a seleção de módulos.
- `/sobre/` mostra a mesma página sempre, mesmo com login. Nesse caso o botão vira "Abrir o sistema".
- A página não exibe dado do banco. As capturas de tela são imagens estáticas feitas com os dados fictícios do `popular_demo`.
- A tela de login tem o link "Conhecer o sistema" de volta para ela.
- As demais páginas continuam exigindo login e redirecionando para `/login/` com `next`.

### Login e seleção

- `LoginView` em `/login/`. Usuário já autenticado é redirecionado.
- Após o login, vai para `/` (`SelecaoView`), que mostra os cartões dos módulos liberados para o perfil. Sem login, a mesma view entrega a apresentação.
- A tela de login tem o botão "Solicitar ajuda aos administradores", que abre um modal com instruções. Não grava nem envia nada.

### Sessão

| Regra | Valor | Onde |
| --- | --- | --- |
| Expira ao fechar o navegador | sempre | `SESSION_EXPIRE_AT_BROWSER_CLOSE` |
| Expira por inatividade | 60 minutos; ajustável pela variável `SESSAO_MINUTOS` | `SESSION_COOKIE_AGE` |
| Cada requisição renova o prazo | sempre | `SESSION_SAVE_EVERY_REQUEST` |

- A validade fica gravada no servidor, junto com a sessão. Não depende de o navegador apagar o cookie.
- Reiniciar o servidor ou publicar uma versão nova não encerra sessões: elas ficam no banco. Isso é intencional.
- Gerar nova senha temporária para um usuário encerra as sessões abertas dele.
- Sessão expirada em página comum: redirecionamento para o login, com retorno à página pedida.
- Sessão expirada em pedido HTMX (um clique em "Salvar", por exemplo): `pedir_login` responde 401 com `HX-Redirect`, e a página inteira vai para o login. Depois de entrar, a pessoa volta para a tela em que estava. Sem isso, a tela de login apareceria dentro do modal.
- O pré-deploy roda `clearsessions`, que apaga do banco as sessões vencidas.

Fora do escopo por ora: aviso de "sua sessão vai expirar", bloqueio por tentativas de login e segundo fator.

### Senha temporária

1. O admin cadastra o usuário em `/usuarios/novo/`. `gerar_senha_temporaria()` cria 10 caracteres sem símbolos ambíguos (sem `0/O`, `1/l/I`).
2. A senha aparece uma única vez (`_senha_temporaria.html`), em resposta marcada como não cacheável.
3. `TrocaSenhaObrigatoriaMiddleware` redireciona qualquer navegação para `/senha/trocar/` enquanto `senha_temporaria` for `True`. Só a troca de senha e o logout ficam liberados. Em pedido HTMX, a resposta é 403 com `HX-Redirect`.
4. `TrocarSenhaView` zera o marcador e registra log.

"Esqueci a senha" usa o mesmo fluxo por `/usuarios/<id>/nova-senha/`. Gerar nova senha derruba as sessões abertas daquele usuário.

### Administração de usuários (`views_admin.py`)

| Rota | Ação | Travas |
| --- | --- | --- |
| `/usuarios/` | Lista com busca, filtro por perfil e status. Padrão: só ativos | |
| `/usuarios/novo/` | Cadastra e mostra a senha temporária | |
| `/usuarios/<id>/editar/` | Edita nome, usuário e perfil | Admin não tira o próprio perfil de admin |
| `/usuarios/<id>/nova-senha/` | Gera nova senha temporária | Não vale para si mesmo |
| `/usuarios/<id>/desativar/` e `/reativar/` | Muda `ativo` | Não desativa a si mesmo |
| `/usuarios/<id>/anonimizar/` | Anonimiza | Não vale para si mesmo; exige confirmação marcada |
| `/log/` | Log de ações com filtros por usuário, ação e período | |

Usuário anonimizado devolve 404 em qualquer rota de edição (`_editavel`).

### Anonimização (`gestao.py`, RF15)

`anonimizar_usuario`, em uma transação:

- `nome` vira "Usuário anonimizado" e `username` vira `anonimizado-<id>`;
- desativa o acesso e torna a senha inutilizável;
- marca `anonimizado = True`;
- com `ANONIMIZAR_LOG = True` (valor atual), troca também o nome nos registros de log dessa pessoa.

É irreversível.

### Log de ações (`logs.py`, RF14)

`registrar_log(usuario, acao)` é chamado à mão nas views e serviços, depois de cada criação ou edição. Não há auditoria automática: view nova que altera dados precisa chamar a função.

## Código compartilhado

| Módulo | Conteúdo |
| --- | --- |
| `permissoes.py` | `perfil_requerido`, `pedir_login`, `PerfilRequeridoMixin`, constantes `ESTOQUE`, `FRETES`, `GESTAO`, `ADMINISTRACAO` |
| `htmx.py` | `eh_htmx`, `pagina_ou_trecho`, `gatilho`, `salvo`, `ir_para` |
| `formatos.py` | `moeda` e `numero` no padrão brasileiro |
| `middleware.py` | `TrocaSenhaObrigatoriaMiddleware` |
| `templates/inosys/base_app.html` | Layout com sidebar, usado por todas as telas internas |
| `templates/inosys/_paginacao.html` | Paginação comum |
| `templates/403.html` | Acesso negado |
| `static/inosys/` | `estilos.css`, logos, `app.js` (comportamento comum a todas as telas) e `usuarios.js` |

## Testes

`contas/tests.py` (login, perfis, troca obrigatória, sessão), `contas/test_comandos.py` (`criar_admin`) e `contas/test_gestao.py` (administração, senha temporária, anonimização, log).
