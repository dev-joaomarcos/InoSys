# Roteiro da demo

Para quem vai apresentar. Duração: cerca de 10 minutos, mais perguntas. Os nomes e números abaixo são os que o comando `popular_demo` cria; se alguém mexer nos dados antes, eles mudam.

## Preparação

### Na véspera

- [ ] Deploy feito e conferido ([deploy-railway.md](deploy-railway.md)).
- [ ] Banco com os dados de demonstração (`popular_demo`) e sem testes manuais por cima.
- [ ] Senha do `admin` já trocada (o primeiro acesso obriga a troca; não deixe isso para a hora).
- [ ] Senhas anotadas em local seguro, fora do repositório.

### Dez minutos antes

- [ ] Abrir a URL. A página de apresentação precisa aparecer com estilo, logo e as capturas de tela.
- [ ] Entrar com `gustavo` e conferir a Visão Geral.
- [ ] Se a tela vier sem estilo, a rede do local está bloqueando CDN (Bootstrap, HTMX e fontes vêm da internet). Plano B: rotear pelo celular.
- [ ] Deixar duas janelas prontas: uma normal e uma anônima, para trocar de usuário sem perder tempo com logout.
- [ ] Zoom do navegador em 110% ou 125% se for projetar.
- [ ] Entrar com os usuários só nesta hora. A sessão cai ao fechar o navegador e após 60 minutos sem uso, então logins feitos na véspera não valem.

### Usuários

| Usuário | Nome | Perfil | Usado em |
| --- | --- | --- | --- |
| `paula` | Paula Ribeiro | Operacional de Estoque | Parte 1 |
| `fabio` | Fábio Lima | Operacional de Fretes | Parte 2 |
| `gustavo` | Gustavo Mendes | Gestor | Parte 3 |
| `admin` | Administrador | Administrador | Parte 4 |

Os três primeiros usam a senha passada ao `popular_demo`.

## Abertura (1 min)

> "A INOVE instala divisórias e forros. Ela tinha dois problemas: não saber quando o material ia acabar e não saber se o frete cobrado batia com o combinado. O InoSys resolve os dois: um controle de estoque que calcula o saldo sozinho e um monitor de fretes que confere o valor de cada entrega."

Faça essa fala com a página de apresentação aberta (o endereço do sistema, sem login): ela mostra o problema, o que o sistema faz e as telas. Depois clique em "Entrar no sistema" e, na tela de login, diga que não existe "criar conta": o acesso é dado pelo Administrador.

Se já estiver logado, a apresentação fica em `/sobre/`.

## Parte 1: Estoque, com `paula` (3 min)

| Passo | O que fazer | O que dizer | Requisito |
| --- | --- | --- | --- |
| 1 | Entrar com `paula` | "A Paula cuida do depósito. Reparem que ela só enxerga o módulo de Estoque." | RF01, RNF05 |
| 2 | Abrir Estoque | "Logo no topo, o sistema avisa: 3 materiais abaixo do mínimo." Aponte Placa de gesso (14 de 20), Perfil guia (8 de 30) e Massa para junta (9 de 15). | RF05 |
| 3 | Registrar **entrada** de 40 un de Placa de gesso | "Chegou material. Ela só informa a quantidade." Ao salvar: o saldo vai a 54, o aviso cai para 2 materiais e a página não recarregou. | RF03 |
| 4 | Tentar **saída** de 100 pç de Perfil guia | "Agora um erro de digitação: tirar 100 quando só há 8." O sistema recusa e diz quanto há. | RF04 |
| 5 | Corrigir para saída de 5, motivo "Uso em produção" | "Toda saída exige motivo." Saldo vai a 3. | RF04 |
| 6 | Aba Movimentações | "Tudo fica no histórico, com data e responsável. Não existe botão de editar nem de apagar: o histórico é imutável." Filtre por um material. | RF06 |

Ponto a reforçar: ninguém digita o saldo. Ele é consequência das movimentações.

## Parte 2: Fretes, com `fabio` (3 min)

| Passo | O que fazer | O que dizer | Requisito |
| --- | --- | --- | --- |
| 1 | Entrar com `fabio` (janela anônima) | "O Fábio só enxerga Fretes." | RNF05 |
| 2 | Aba Entregadores | "Cada entregador tem um valor por quilômetro. O João cobra R$ 2,50; o Carlos, R$ 3,20." | RF07 |
| 3 | Nova entrega: João Batista, 30 km | "Vejam o valor sugerido aparecendo enquanto eu digito: 30 × 2,50 = R$ 75,00." Salve sem valor cobrado, status Pendente. | RF08 |
| 4 | Editar essa entrega: status Concluída, valor cobrado R$ 90,00 | "O entregador cobrou 90. O sistema marca a divergência de R$ 15,00." O indicador "Divergência de valor" passa de 4 para 5. | RF09, RF10, RF12 |
| 5 | Mostrar a entrega "Obra em Osasco" (Carlos) | "Divergência também pode ser para menos: aqui foram cobrados R$ 6,00 abaixo do sugerido." | RF12 |
| 6 | Filtrar por status ou por entregador | "O histórico tem filtro por entregador, status e período." | RF11 |

Ponto a reforçar: o sistema não julga a diferença, só garante que ela seja vista.

## Parte 3: Gestão, com `gustavo` (2 min)

| Passo | O que fazer | O que dizer | Requisito |
| --- | --- | --- | --- |
| 1 | Entrar com `gustavo` | "O Gustavo é gestor: vê os dois módulos e ganha a Visão Geral." | RNF05 |
| 2 | Visão Geral | "Em uma tela: materiais em falta, entregas em aberto, quanto foi cobrado nos últimos 30 dias e as divergências." Mostre o gráfico de sugerido × cobrado por entregador. | RF12 |
| 3 | Relatórios → Movimentações | "Quanto de cada material entrou e saiu, separado por motivo: uso, perda ou ajuste." | RF12 |
| 4 | Relatórios → Fretes, marcar "só divergências" | "E aqui só as entregas com diferença, com o total por entregador." | RF12 |

Números de referência antes de qualquer alteração: 3 materiais em falta, 5 entregas em aberto, 15 concluídas, R$ 1.176,45 cobrados, 4 divergências. As partes 1 e 2 mudam esses números; isso é esperado e mostra que o painel é ao vivo.

## Parte 4: Administração, com `admin` (2 min)

| Passo | O que fazer | O que dizer | Requisito |
| --- | --- | --- | --- |
| 1 | Entrar com `admin`, abrir Administração | "Só o Administrador chega aqui." | RNF05 |
| 2 | Novo usuário (ex.: "Marina Costa", perfil Estoque) | "O sistema gera uma senha temporária e mostra uma única vez." Copie a senha. | RF13 |
| 3 | Em janela anônima, entrar com a nova usuária | "No primeiro acesso ela é obrigada a trocar a senha. Nenhuma outra tela abre antes disso." | RF01, RNF04 |
| 4 | Voltar ao admin, aba Log de ações | "Tudo o que fizemos nesta demo está registrado: quem e quando." | RF14 |
| 5 | Anonimizar a usuária recém-criada | "Se alguém sai da empresa e pede a remoção dos dados, o nome é trocado por um valor genérico. O histórico fica, a identificação some. Não tem volta." | RF15 |

## Fechamento (30 s)

> "Resumindo: saldo calculado pelo sistema, frete conferido automaticamente, um acesso para cada função e tudo registrado. Está publicado e funcionando neste endereço."

## Perguntas prováveis

| Pergunta | Resposta |
| --- | --- |
| Por que não tem "esqueci minha senha" por e-mail? | São poucos usuários, todos na mesma empresa. O Administrador gera uma nova senha temporária. Isso evita depender de um serviço de e-mail. |
| E se dois funcionários registrarem saída do mesmo material ao mesmo tempo? | O sistema trava o registro do material durante a operação. A segunda saída só é avaliada depois da primeira, então o saldo nunca fica negativo. |
| Por que guardar o saldo em vez de somar as movimentações? | Para a tela abrir rápido. O saldo só é alterado pelo próprio registro da movimentação, na mesma transação, então os dois nunca divergem. Há um teste automatizado que confere isso. |
| Como as senhas são guardadas? | Com hash, pelo mecanismo padrão do Django. Ninguém, nem o Administrador, consegue ler a senha de um usuário. |
| Dá para apagar um material ou um entregador? | Não. Eles são desativados. Assim o histórico de movimentações e entregas continua íntegro. |
| O sistema calcula a distância da entrega? | Não. A distância é informada por quem registra. Integração com mapas ficou fora do escopo. |
| Qual a tolerância para considerar divergência? | Nenhuma: qualquer diferença aparece. Definir uma tolerância é uma decisão de negócio em aberto. |
| Os relatórios podem ser exportados? | Ainda não, são consultados em tela. É uma evolução prevista. |
| O log mostra o que foi alterado? | Hoje mostra quem, o tipo de ação e quando. Detalhar o registro alterado é uma melhoria já mapeada. |
| Funciona no celular? | Sim. O menu vira um painel deslizante e as tabelas rolam na horizontal. (Mostre com F12, se der tempo.) |
| E se alguém esquecer o sistema aberto? | A sessão expira após 60 minutos sem uso e ao fechar o navegador. O prazo é conferido no servidor. |
| Como é testado? | Há 106 testes automatizados cobrindo regras de estoque, cálculo de frete, permissões e relatórios. |
| Onde está hospedado? | No Railway, com banco PostgreSQL. |

## Se algo der errado

| Problema | O que fazer |
| --- | --- |
| Tela sem estilo | Rede bloqueando CDN. Trocar para o roteador do celular. |
| O sistema voltou para a tela de login | Sessão expirada por 60 minutos sem uso. Entrar de novo; a tela anterior reabre. |
| Erro ao salvar (403) | Página aberta há muito tempo. Recarregar e tentar de novo. |
| Site fora do ar | Ter prints das telas principais como reserva, ou rodar local: `migrate`, `criar_admin`, `popular_demo`, `runserver`. |
| Dados bagunçados por ensaio anterior | O `popular_demo` só roda em banco vazio. É preciso recriar o banco no Railway e fazer novo deploy. Faça os ensaios em ambiente local. |
