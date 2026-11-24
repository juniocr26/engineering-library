# Consulta de decorações no Fastify: guardas ordenadas e alternativa explícita

Correção experimental escrita pelo Codex e revisada na fonte congelada, pendente de aprovação humana. Fonte: Fastify na revisão `825d7722e4932a39193729997c76535d0a963b6b`, `lib/decorate.js`. O baseline real do agente local é `fastify-checkrequestexistence`. Ele continha somente o wrapper de requisição. Este capítulo amplia explicitamente a evidência para o wrapper de resposta, auxiliares compartilhados, nomes importados e aliases de exportação do mesmo arquivo. Nenhum módulo Fastify, servidor HTTP ou código de aplicação inspecionado foi executado.

## O wrapper testa um nome fornecido

A função `checkRequestExistence` recebe um parâmetro chamado `name`. Sua primeira condição é `name && hasKey(this[kRequest], name)`. Um resultado de valor lógico verdadeiro alcança a expressão escrita de retorno `true`. Somente quando esse ramo não é seguido a função alcança a segunda condição, `name && hasInstanceProperty(this[kRequest], name)`. Esse ramo também retorna a expressão true escrita quando sua condição tem valor lógico verdadeiro.

O nome participa das duas condições de curto-circuito. Um nome de valor lógico falso impede a avaliação do operando auxiliar correspondente em cada guarda. Essa observação não determina o resultado final da função: ainda existe uma instrução final. Ela retorna `checkExistence(this[kRequest].prototype, name)`. O wrapper não contém um retorno falso incondicional para um nome omitido. O baseline neural inventou precisamente essa alternativa.

O acesso entre colchetes também faz parte da distinção de papéis. A fonte não passa um objeto de requisição como argumento explícito dessa função. Ela obtém um alvo por uma propriedade do receptor em execução e passa o nome fornecido aos auxiliares. O valor da chave importada e o receptor efetivo não devem ser inferidos apenas pelo nome da função.

## O caminho de resposta é um contrato irmão

A função `checkReplyExistence` tem a mesma sequência usando `this[kReply]`. Sua chamada final aponta para o protótipo correspondente. Isso corrobora o padrão escrito, mas pertence à mesma família de consulta de decorações. Dois wrappers semelhantes não estabelecem transferência independente nem provam como todo chamador vincula seus receptores.

O arquivo obtém os dois nomes de chave por uma importação relativa e exporta os wrappers como `existRequest` e `existReply`. Essas são relações explícitas da fonte. Os aliases não provam que um servidor registrou ou chamou as funções em determinada execução. Esta inspeção não carrega o módulo importado nem cria requisições ou respostas.

## Os dois auxiliares iniciais examinam estruturas diferentes

O auxiliar `hasKey` verifica o valor lógico de uma propriedade `props`. Quando presente, chama a operação de busca no estilo de array dessa propriedade com um predicado que compara uma chave armazenada com o nome fornecido; caso contrário, a alternativa escrita é false. A fonte não valida que a propriedade tenha todos os métodos esperados em execução, e um acesso a propriedade ou uma operação chamada não é automaticamente livre de efeitos.

O auxiliar `hasInstanceProperty` começa com um cursor local definido pelo primeiro argumento. Enquanto o cursor tem valor lógico verdadeiro, testa uma coleção de propriedades e sua operação de pertinência. Uma condição bem-sucedida retorna true. Caso contrário, atribui `k = k.parent` e continua; sair do laço alcança false. Essa é uma travessia específica de um campo de pai. Ela não equivale a percorrer automaticamente protótipos JavaScript, e o corpo não demonstra detecção de ciclos ou término garantido para objetos arbitrários.

## O auxiliar final não justifica falso para nome ausente

O auxiliar `checkExistence` distingue um nome de valor lógico verdadeiro do outro caminho. Para o primeiro caso, combina testes de pertinência e uma chamada ao auxiliar de chaves armazenadas. No outro caminho, a expressão escrita é `instance in this`. Essa expressão não é a constante false. A validade do receptor e o ponto alcançado continuam como precondições explícitas.

Se esse ramo for alcançado pela chamada simples em modo estrito mostrada, `this` será `undefined`; aplicar `in` com esse operando à direita lança `TypeError`. Esse é um caminho condicional derivado da linguagem, corroborado por um exemplo sintético próprio, não uma execução observada do Fastify. As regras estão especificadas em [vínculo estrito de this](https://tc39.es/ecma262/2026/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinarycallbindthis) e [avaliação de operadores relacionais](https://tc39.es/ecma262/2026/multipage/ecmascript-language-expressions.html#sec-relational-operators-runtime-semantics-evaluation).

Os wrappers não fazem atribuição explícita à estrutura alvo de requisição ou resposta em seus próprios corpos. Isso não prova pureza global: chamadas auxiliares, getters e comportamento dos objetos em execução continuam como dependências separadas. A correção preserva a ordem e a alternativa exata, mantendo essas fronteiras visíveis.

O produtor independente de fonte agora acrescenta um pacote opcional de guardas ordenadas para esses wrappers. Seu parágrafo original da primeira guarda não mudou, e o pacote novo registra expressões escritas sem fornecer semântica ausente dos auxiliares. O baseline real do modelo continua rejeitado; este capítulo e o pacote determinístico são artefatos separados, sem treinamento neural, publicação ou promoção automática a dados de treinamento aprovados.
