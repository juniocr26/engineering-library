# Fastify: execução de hooks e limites da validação

Capítulo experimental escrito pelo Codex após revisão da fonte. É um rascunho de correção, não saída inalterada do modelo local. Aprovação humana factual e bilíngue pendente; não é resposta positiva para treinamento.

Revisão da fonte: `825d7722e4932a39193729997c76535d0a963b6b`.

## 1. Nomes de hooks indexam arrays de funções

`Hooks` inicializa arrays como `onRequest`, `preValidation`, `onReady`, `onListen` e `preClose`. Esses campos armazenam listas de funções; as atribuições não definem métodos com esses nomes. O construtor cria listas vazias e não invoca uma função de hook. [lib/hooks.js:40–56](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L40-L56)

`Hooks.prototype.validate` verifica um nome de hook em string, um array em `this[hook]` e uma função como handler, com os lançamentos explícitos correspondentes. `Hooks.prototype.add` chama essa validação e executa `this[hook].push(fn)`. Acrescenta a função, sem adicionar um segundo par hook/handler ou uma cópia do registro inteiro. [lib/hooks.js:60–66](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L60-L66), [lib/hooks.js:68–71](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L68-L71)

`buildHooks` constrói `new Hooks()` e copia os arrays herdados listados usando `slice()`. Depois atribui novos arrays vazios a `onReady`, `onListen` e `preClose`. Os arrays copiados são contêineres distintos, enquanto a fonte não contém clonagem profunda de suas funções. As três listas reiniciadas não devem ser descritas como funções herdadas. [lib/hooks.js:73–91](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L73-L91)

## 2. O despacho passa pelo iterador fornecido

`hookRunnerGenerator` retorna um executor com índice `i = 0` e o inicia por `next()`. Em `next(err)`, um erro ou o fim da lista chama `cb(err, request, reply)` e retorna. No outro caminho, invoca `iterator(functions[i++], request, reply, next)` dentro de um bloco try. O chamado direto é o iterador fornecido; portanto, o corpo sozinho não estabelece como esse iterador invoca um hook nem quais argumentos lhe fornece. [lib/hooks.js:230–266](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L230-L266)

O mesmo executor captura um lançamento síncrono do iterador e chama `cb(error, request, reply)`. Um resultado verdadeiro em contexto lógico com `then` do tipo função recebe `handleResolve` e `handleReject`. A resolução chama `next()`; a rejeição substitui um erro falso em contexto lógico por `new FST_ERR_SEND_UNDEFINED_ERR()` e chama `cb`. Para um resultado fora desse ramo de thenable, o corpo não faz avanço automático adicional: o iterador fornecido recebeu a continuação. [lib/hooks.js:230–266](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L230-L266)

## 3. Hooks de aplicação combinam registro, filhos e conclusão

`hookRunnerApplication` acompanha seus hooks com `i` e as instâncias filhas com `c`. Registra `boot(wrap(hooks[i++], server))` e chama `next()`. Após o fim de sua própria lista, visita recursivamente os filhos por `hookRunnerApplication(hookName, boot, child, next)`. O corpo fornecido expõe a ordem de registro e percurso; o agendamento da execução permanece no mecanismo externo de inicialização. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

Quando as duas listas terminam, o caso sem hooks nem filhos chama `exit()` diretamente. No outro caso, o corpo registrado de `manageTimeout(err, done)` chama `exit(err)` antes de `done(err)`. O caminho de saída converte `AVV_ERR_READY_TIMEOUT` por `FST_ERR_HOOK_TIMEOUT`; outros códigos mapeados usam `AVVIO_ERRORS_MAP` e `appendStackTrace`. Chama `cb(err)` no caminho de erro ou `cb()` no outro caminho. O mapa e as chamadas de conversão ocorrem nesta função citada, sem se limitarem a seu fragmento final. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

O invólucro primeiro encaminha um erro de entrada a `done(err)`. Para `fn.length === 1`, a chamada escrita é `fn.call(server, done)`: essa forma de chamada fornece o servidor como receptor e a função de conclusão como argumento. As demais funções usam `fn.call(server)`. Um thenable retornado recebe `ret.then(done, done)`; um lançamento síncrono é atribuído a `err`, e o caminho restante chama `done(err)`. Essa fonte não passa o servidor como argumento posicional comum ao hook. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

## 4. Hooks de escuta usam uma continuação como coordenadora

`onListenHookRunner` captura a quantidade de hooks, inicia `next()` e registra um erro verdadeiro em contexto lógico por `server.log.error(err)`. Quando seus hooks terminam, percorre os filhos e chama `onListenHookRunner(child)`. No outro caminho, chama `wrap(hooks[i++], server, next)`. A função externa não tem instrução de retorno que exponha ao chamador o resultado do invólucro assíncrono. [lib/hooks.js:183–228](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L183-L228)

A função aninhada `async function wrap` usa o caminho com callback para `fn.length === 1`, chamando `fn.call(server, done)` dentro de try/catch e retornando em seguida. Esse ramo não aguarda um valor retornado. O outro caminho chama `fn.call(server)`, associa `ret.then(done, done)` a um thenable e, no outro caso, chama `done()`. Erros síncronos são encaminhados a `done(error)`. Apenas declarar o invólucro assíncrono não faz o ramo com callback aguardar sua função de conclusão. [lib/hooks.js:183–228](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L183-L228)

## 5. A validação de parâmetros separa caminhos síncronos e thenables

`validateParam` retorna `false` quando `validatorFunction == null`, antes de ler `request[paramName]`. No outro caso, lê essa parte da requisição e converte somente `undefined` em `null` para o argumento de dados. Um `validatorFunction.schemaEnv` verdadeiro em contexto lógico seleciona a chamada com `parentData: request` e `parentDataProperty: paramName`; a outra chamada recebe somente os dados. O ambiente do esquema seleciona uma forma de chamada; não é passado como argumento de esquema. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

Um lançamento síncrono dentro do bloco try de validação mostrado atribui `err.statusCode = 500` e retorna `err`. Nesse limite, trata-se de um objeto de erro retornado. O catch não justifica garantia de ausência de exceções para todo getter posterior, implementação de thenable ou interação com o chamador. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

Para um resultado verdadeiro em contexto lógico com `then` do tipo função, a cadeia retornada mapeia `res === false` para `validatorFunction.errors` e qualquer outro valor de resolução para `false`. Seu tratador de rejeição retorna `err`. Esse ramo não desembrulha o conteúdo resolvido pela função de resposta síncrona: propriedades chamadas `error` ou `value` no conteúdo não são usadas aqui para substituir a parte da requisição nem injetar um resultado de validação. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

O caminho síncrono de `answer(ret)` primeiro mapeia `ret === false` para `validatorFunction.errors`. Em seguida, retorna um `ret.error` verdadeiro em contexto lógico. Somente após essas guardas um objeto que satisfaça `'value' in ret` atribui `request[paramName] = ret.value`; o retorno final é `false`. O teste de presença inclui propriedades herdadas e não exige verificação de propriedade própria. Outros valores falsos em contexto lógico não são automaticamente erros de validação. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

## 6. O invólucro de erro preserva alguns campos e substitui outros

`wrapValidationError` primeiro testa `result instanceof Error`. Nesse ramo, mantém campos existentes verdadeiros em contexto lógico e, nos demais casos, fornece a `statusCode` o valor `400`, a `code` o valor `FST_ERR_VALIDATION` e a `validationContext` o valor `dataVar`; depois retorna o mesmo objeto. O operador de fallback é OU lógico, portanto não se limita a campos nulos ou indefinidos. Esse ramo não acrescenta uma nova atribuição do conteúdo da validação. [lib/validation.js:508–522](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L508-L522)

O outro ramo chama `schemaErrorFormatter(result, dataVar)` com dois argumentos. Aplica os mesmos valores alternativos de status/código e então atribui `error.validation = result` e `error.validationContext = dataVar` antes de retornar `error`. A atribuição de contexto aqui substitui um valor existente. O código fornecido não lê status nem código do rótulo de contexto e não estabelece a implementação do formatador nem garantia de retorno bem-sucedido. [lib/validation.js:508–522](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L508-L522)

## 7. Ordem de validação, flags de salto e o sentinela false

`validate` define `runExecution = execution === undefined`. Seu caminho rápido inicial retorna `false` somente quando isso é verdadeiro e as quatro posições selecionadas de esquema são `undefined`. A ordem seguinte é params, body, query e headers. As três primeiras etapas respeitam `execution.skipParams`, `execution.skipBody` e `execution.skipQuery` quando não se inicia uma execução nova; a etapa de headers não tem flag de salto correspondente nesse corpo. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

Na validação do corpo, uma função em `context[bodySchema]` é usada diretamente. No outro caso, um contêiner de esquemas verdadeiro em contexto lógico é indexado por `request.mediaType`; somente uma entrada correspondente verdadeira substitui o validador inicialmente nulo. Essa função não analisa um cabeçalho de tipo de conteúdo, não normaliza suas letras nem inventa um esquema para um tipo de mídia sem correspondência. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

Cada etapa chama `validateParam` e inspeciona um resultado verdadeiro em contexto lógico. Um resultado sem `then` do tipo função é passado a `wrapValidationError`; um resultado thenable é passado ao auxiliar assíncrono específico da etapa e retornado. Os corpos dos auxiliares não são fornecidos aqui. Os dados da consulta são lidos por `query`, enquanto seu rótulo de contexto de erro é `querystring`. O `false` final marca o caminho que não encontrou resultado de validação verdadeiro em contexto lógico; não é um sinal incondicional de falha. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

## Evidência e limites

As definições citadas foram inspecionadas estaticamente. Nenhuma aplicação, banco, servidor ou suíte de testes do projeto externo foi executada para estabelecer comportamento em execução. Auxiliares externos exigem sua própria fonte e suas premissas. Estes capítulos ampliam e corrigem rascunhos de pesquisa; não foram colocados no catálogo público. Licenças das fontes e citações/hashes exatos estão preservados na evidência da campanha.

Licença do projeto fonte: [LICENSE](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/LICENSE). O texto exato da licença e seu checksum estão preservados com a evidência da fonte.
