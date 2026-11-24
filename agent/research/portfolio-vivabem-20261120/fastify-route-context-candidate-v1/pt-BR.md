# Fastify: registro de rotas, prefixos e HEAD gerado

Este capítulo descreve fontes selecionadas da revisão `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3` do Fastify. É uma revisão histórica, sem afirmar que representa o checkout mais recente da coleção. O tema é o contexto de registro ao redor da condição de prefixo na raiz, não todo o processamento da requisição ou a implementação do roteador. Este é um candidato de pesquisa escrito manualmente a partir das fontes, sem aprendizagem neural, aprovação do proprietário ou registro de treinamento. A licença fixada em `LICENSE` foi preservada com as evidências.

## Entradas e responsabilidade

Em `fastify.js:197-231`, os métodos públicos abreviados chamam `router.prepareRoute.call`; o método abreviado de HEAD fornece `HEAD` escalar, enquanto `all` fornece `this.supportedMethods`. A entrada de rota estendida chama `router.route.call` com um objeto de opções. Essas entradas públicas selecionadas não fornecem o argumento interno `isFastify`. A ligação está escrita entre arquivos: `fastify.js:51,116` importa e invoca `buildRouting`, e `lib/route.js:93-126,726` retorna as funções de registro e exporta o construtor. A instância da biblioteca de roteamento dentro desse construtor é um `router` local diferente do objeto retornado a `fastify.js`.

O observador léxico localiza declarações locais, incluindo `prepareRoute` chamando `route` e `addNewRoute` chamando `prepareRoute`. Ele deixa chamadas por propriedades como `router.on` sem resolução. A ligação entre arquivos foi revisada manualmente; o observador não a inferiu automaticamente. Uma associação léxica ou expressão `.call` não prova que o destino em execução seja insubstituível.

## Opções, normalização e erros anteriores

Em `lib/route.js:143-170`, `prepareRoute` verifica a URL e determinadas combinações de opções e manipulador. Copia as opções com `Object.assign` e então fornece `method`, `url`, `path` e o manipulador selecionado. Assim, nesse caminho, o argumento de método copiado tem precedência sobre uma propriedade das opções. O argumento separado `isFastify` é encaminhado a `route`.

Em `lib/route.js:206-245`, `route` primeiro verifica se o registro já foi iniciado, faz uma cópia superficial das opções em `opts` e atribui `opts.isGeneratedHeadRoute = isFastify === true`. Fornecer uma propriedade de opções com esse nome não evita a atribuição no caminho público selecionado. Ausência de manipulador, manipulador de erros personalizado inválido, validação do limite de corpo e validação do tempo limite do manipulador podem interromper o registro antes do processamento do método ou da decisão sobre prefixos. Este capítulo não enumera todas as regras de validação ou todos os erros posteriores.

Para um método escalar, `normalizeAndValidateMethod` exige uma string, converte para maiúsculas e consulta os dois conjuntos de métodos suportados (`lib/route.js:637-647`). Tipo inválido e método não suportado usam `FST_ERR_ROUTE_METHOD_INVALID` e `FST_ERR_ROUTE_METHOD_NOT_SUPPORTED`. `validateSchemaBodyOption` rejeita um esquema de corpo para um método do conjunto sem corpo (`lib/route.js:650-653`); esses conjuntos são dependências, não uma lista exaustiva de métodos demonstrada aqui.

Para um array, cada elemento indexado passa pela mesma normalização e validação de esquema. O array continua sendo um array: um array HEAD de um elemento não se torna escalar. As atribuições indexadas também afetam o compartilhamento: a cópia superficial das opções mantém a referência ao array de métodos original, portanto esse código pode alterar seus elementos. Um array vazio pula o laço; isso não garante sucesso no registro posterior. Exceções ou entradas não suportadas interrompem o caminho selecionado antes das decisões seguintes.

## Prefixos da raiz e rotas geradas

A variável local `shouldExposeHead` usa a opção por rota `exposeHeadRoute` quando ela não é nula nem indefinida; caso contrário, usa `globalExposeHeadRoutes` do construtor. A configuração atribui esse valor global a partir de `options.exposeHeadRoutes` (`lib/route.js:98-109,226`). A detecção de GET e HEAD usa igualdade escalar ou pertencimento ao array após a normalização. Com exposição habilitada e GET detectado, `headOpts` é uma cópia superficial das opções originais (`lib/route.js:247-248`), não uma cópia profunda de todo o estado mutável aninhado.

Em `lib/route.js:250-274`, um caminho raiz com prefixo não vazio entra no ramo de seleção de barras somente quando a marca de rota gerada é falsa. Registros públicos explícitos de HEAD podem entrar nesse ramo, com método escalar ou array. `prefixTrailingSlash` seleciona a forma com barra, sem barra ou o caminho padrão de ambas as formas. No caso de ambas, o segundo registro local ainda depende de `ignoreTrailingSlash`, `ignoreDuplicateSlashes` e de o prefixo já terminar em barra. Outros caminhos têm um ajuste separado quando o prefixo termina em barra. A fonte não afirma que todo prefixo produz dois registros.

Dentro de `addNewRoute`, campos de URL e caminho são atualizados, e o registro sem a marca de prefixação executa hooks `onRoute` antes de `router.on` (`lib/route.js:279-303,365`). Esses callbacks recebem `opts`; seus efeitos e o comportamento do roteador externo ficam fora desta comprovação léxica selecionada. As marcas calculadas anteriormente não garantem que callbacks arbitrários preservem todas as opções. A captura de erro da inserção no roteador também distingue o contexto de rota gerada ao decidir se relança o erro (`lib/route.js:366-377`); isso não garante que todos os erros de registro sejam ignorados.

A construção automática de HEAD selecionada depende de exposição habilitada, GET presente, HEAD ausente e nenhum manipulador de HEAD já encontrado (`lib/route.js:361-362,457-459`). Ela chama `prepareRoute` com `HEAD` escalar, o caminho local, manipuladores de envio preparados e `isFastify: true`. Essa rota recursiva selecionada recebe a marca de geração e pula a divisão do prefixo raiz. Ela não constrói um método em array. A afirmação vale para o ponto de construção selecionado, não como impossibilidade global em JavaScript modificado dinamicamente.

## Fragmento ilustrativo de registro

Dada uma instância Fastify adequadamente inicializada como `app`, este fragmento declara uma rota explícita com array HEAD sob um prefixo. Ele não invoca a função, inicia um servidor ou demonstra bytes reais de resposta. Ilustra um registro explícito, não a API interna de HEAD automático.

```js
function defineRoutes(app) {
  app.register(function prefixed(scope, _options, done) {
    scope.route({
      method: ['HEAD'],
      url: '/',
      handler(_request, reply) { reply.send(); }
    });
    done();
  }, { prefix: '/api' });
}
```

Somente a sintaxe do fragmento é verificada neste trabalho de pesquisa. Tipagem do pacote, ciclo de vida do plugin, inserção de rotas e comportamento de rede não são executados. O percurso das fontes explica por que o formato de array sobrevive à normalização selecionada e por que apenas opções públicas não marcam esse registro como gerado.

## Testes escritos e limites das evidências

O arquivo selecionado `test/route-prefix.test.js:395-425` contém asserções para GET nas duas formas prefixadas. O arquivo selecionado `test/http-methods/head.test.js:110-126` registra `['HEAD', 'GET']`; suas asserções correspondentes de injeção estão mais adiante nesse arquivo. São evidências de testes escritos, não testes executados nesta campanha. Os dois casos não demonstram toda combinação de HEAD explícito, métodos em array, opções de prefixo e mutação por hooks. Não houve instalação de dependências, inicialização de servidor, migrações ou execução de testes upstream. Os resultados das suítes de referência da campanha pertencem à Engineering Library e não podem ser atribuídos a esses testes upstream.

## FAQ

**Todo método HEAD pula o ramo do prefixo raiz?** Não. O ramo selecionado verifica a marca de geração. Registros públicos explícitos de HEAD podem entrar nele; a construção automática selecionada fornece a marca interna.

**Uma propriedade das opções basta para marcar uma rota pública como gerada?** Não no caminho público selecionado. O argumento interno separado controla a atribuição, que sobrescreve essa propriedade das opções.

**Um array vira escalar depois da normalização?** Não. O laço selecionado substitui cada elemento e mantém o array; a cópia superficial não o isola das opções originais.

**Essas fontes provam que as duas formas de prefixo sempre funcionam?** Não. As escolhas locais de barras e opções de ignorar variam, os hooks posteriores e a inserção no roteador importam, e os testes escritos não foram executados aqui.

**A referência a uma função local no observador garante um grafo de chamadas em execução?** Não. Ela identifica declarações léxicas delimitadas e a função à qual cada callback pertence. Propriedades, aliases, associações importadas e substituição em execução exigem evidências adicionais.

## Preservação e incerteza

O experimento anterior da condição isolada permanece preservado; este capítulo acrescenta contexto das fontes sem reinterpretar suas dezesseis observações booleanas como execuções de servidor. Todas as seleções de fontes, os dois arquivos reais de idioma, observações léxicas e registros de revisão são artefatos de pesquisa separados. Repositórios externos, catálogo ativo de documentação, código de produção e testes permanentes permanecem inalterados. A exposição em desenvolvimento impede afirmar uma avaliação de família independente. Este candidato exige revisão completa das fontes e dos dois idiomas e depois revisão do proprietário; não é Gold, não foi publicado e não autoriza treinamento.
