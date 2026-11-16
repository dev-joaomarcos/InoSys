# Como o InoSys funciona, em linguagem simples

Este texto é para quem não é da área técnica. Ele explica o sistema do jeito que você explicaria a um colega novo no primeiro dia: com exemplos do dia a dia e sem jargão. Quando um termo técnico aparecer, ele vem explicado na mesma frase.

## O problema que ele resolve

A INOVE instala divisórias e forros. Para isso ela precisa de duas coisas funcionando bem:

1. **Material no depósito.** Se acabar placa de gesso no meio de uma obra, a obra para.
2. **Entregas com custo justo.** Quem leva o material até a obra é um entregador pago por quilômetro. Sem controle, ninguém sabe se o valor cobrado bate com o combinado.

Antes, isso ficava em caderno, planilha e memória. O InoSys junta as duas coisas num lugar só, acessível pelo navegador.

## A ideia central: dois cadernos que fazem a conta sozinhos

Pense no InoSys como dois cadernos inteligentes.

### Caderno 1: o estoque

Imagine uma prateleira com uma etiqueta para cada material: "Placa de gesso: 14 unidades". Toda vez que chega ou sai material, alguém anota no caderno:

- **Entrada:** "chegaram 50 placas". A etiqueta passa de 14 para 64.
- **Saída:** "saíram 10 placas para a obra". A etiqueta passa de 64 para 54.

A pessoa só anota o que aconteceu. Quem atualiza a etiqueta é o sistema. Ninguém digita o saldo à mão, e por isso ninguém erra o saldo.

Três regras protegem esse caderno:

- **Não dá para tirar o que não existe.** Se há 14 placas, o sistema recusa uma saída de 20 e avisa quanto há.
- **O que foi anotado não se apaga.** Cada entrada e saída fica no histórico para sempre, com a data e o nome de quem anotou. Errou? Faz-se uma nova anotação corrigindo, como num livro-caixa.
- **Toda saída diz o motivo:** uso em produção, perda ou dano, ou ajuste de inventário.

Cada material também tem uma **quantidade mínima**. Se o mínimo de placas é 20 e só restam 14, o sistema destaca esse material com um aviso de "estoque baixo". É a luz de combustível do carro: não impede nada, mas avisa que é hora de comprar.

### Caderno 2: os fretes

Cada entregador tem um preço combinado por quilômetro. O João, por exemplo, cobra R$ 2,50 por km.

Quando alguém registra uma entrega de 40 km feita pelo João, o sistema faz a conta: 40 × 2,50 = **R$ 100,00**. Esse é o **valor sugerido**, isto é, quanto a entrega deveria custar.

Depois, anota-se o **valor cobrado**, que é quanto o entregador de fato pediu. Se ele cobrou R$ 120,00, o sistema marca a entrega como **divergência**: uma diferença de R$ 20,00 que alguém precisa olhar. Pode haver um bom motivo (pedágio, espera na obra) ou pode ser um erro. O sistema não julga. Ele só garante que a diferença não passe despercebida.

Cada entrega também tem uma situação: **pendente**, **em andamento** ou **concluída**.

## Quem usa: quatro crachás

Como num prédio em que cada crachá abre certas portas, cada pessoa tem um **perfil** que define o que ela vê:

| Perfil | O que consegue abrir |
| --- | --- |
| Operacional de Estoque | Só o caderno de estoque |
| Operacional de Fretes | Só o caderno de fretes |
| Gestor | Os dois cadernos, o painel de visão geral e os relatórios |
| Administrador | Tudo acima, e ainda o cadastro de pessoas e o registro de ações |

Quem cuida do depósito não precisa ver valores de frete, e vice-versa. Menos tela, menos confusão, menos risco.

## Como alguém entra no sistema

Não existe botão de "criar conta". Funciona como a portaria de uma empresa:

1. O Administrador cadastra a pessoa e o sistema gera uma **senha provisória**, mostrada na tela uma única vez.
2. O Administrador entrega essa senha à pessoa.
3. No primeiro acesso, o sistema obriga a pessoa a trocar a senha por uma só dela. Enquanto não trocar, nenhuma outra tela abre.

Esqueceu a senha? O mesmo caminho: o Administrador gera outra provisória. Não há envio de e-mail, porque são poucas pessoas e todas trabalham perto umas das outras.

As senhas não ficam guardadas de forma legível. O sistema guarda só uma "impressão digital" embaralhada de cada senha. Nem o Administrador consegue ler a senha de alguém.

## O que o gestor enxerga

O gestor tem um **painel de visão geral**, parecido com o painel de um carro. Ele mostra de relance:

- quantos materiais estão com estoque baixo, e quais;
- quantas entregas estão em aberto;
- quanto foi cobrado em fretes nos últimos 30 dias;
- quantas entregas tiveram divergência, e um gráfico comparando valor sugerido e valor cobrado por entregador.

Há também os **relatórios**, que respondem a perguntas como "quanto de cada material entrou e saiu neste mês, e por qual motivo?" ou "quais entregas do João tiveram diferença de valor?".

## Segurança e privacidade

- **Registro de ações.** Toda vez que alguém cria ou altera algo, o sistema anota quem foi e quando. Só o Administrador vê esse registro. É a câmera da portaria: está ali para quando for preciso conferir.
- **Nada some.** Materiais, entregadores e pessoas não são apagados, só **desativados**. O histórico continua inteiro.
- **Anonimização.** Se alguém sai da empresa e pede que seus dados pessoais sejam removidos (direito previsto na LGPD, a lei brasileira de proteção de dados), o Administrador pode trocar o nome da pessoa por "Usuário anonimizado". O histórico do que foi feito permanece, mas sem identificar quem fez. Essa operação não tem volta.

## Como ele funciona por dentro

Pense num restaurante.

- **O navegador é o salão.** É onde você senta, vê o cardápio e faz o pedido. No InoSys, são as telas.
- **O servidor é a cozinha.** O pedido chega, alguém confere se você pode pedir aquilo (o seu crachá), prepara e devolve o prato pronto. No InoSys, esse cozinheiro é um programa escrito em Python com uma ferramenta chamada Django.
- **O banco de dados é a despensa com o livro de registros.** Tudo o que precisa ser lembrado amanhã fica guardado ali: materiais, movimentações, entregas, pessoas.

Dois detalhes desse restaurante:

- **As contas são feitas na cozinha, nunca no salão.** O saldo do estoque e o valor sugerido do frete são calculados pelo servidor. Mesmo que alguém tente adulterar a tela no próprio computador, o número que vale é o da cozinha.
- **O garçom troca só o prato, não a mesa inteira.** Quando você salva um material, o sistema atualiza apenas a lista na tela, sem recarregar a página toda. Por isso o uso parece rápido.

A cozinha é organizada em quatro bancadas, cada uma com uma responsabilidade: **contas** (pessoas, senhas e crachás), **estoque**, **fretes** e **relatórios**. A bancada de relatórios é a única que olha para as outras: ela junta os dados do estoque e dos fretes para montar o painel do gestor.

## Onde o sistema mora

O InoSys fica hospedado na internet, num serviço chamado Railway. É como alugar a cozinha e a despensa em vez de construí-las: a equipe não precisa cuidar de computador físico, e qualquer pessoa autorizada acessa pelo navegador, do computador ou do celular.

## O que ele não faz

Saber os limites faz parte de entender o sistema:

- não envia e-mails nem mensagens;
- não guarda fotos ou comprovantes de entrega;
- não exporta relatórios para planilha ou PDF (eles são vistos na tela);
- não calcula a distância sozinho: quem registra a entrega informa os quilômetros;
- não faz pedido de compra: ele avisa que o material está acabando, e a compra continua com as pessoas.

## Resumo em uma frase

O InoSys é um caderno de estoque que nunca erra a soma e um caderno de fretes que confere a conta do entregador, com um crachá para cada pessoa e um painel para o gestor ver tudo de uma vez.
