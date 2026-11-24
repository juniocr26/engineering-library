# Tratamento de barra final no prefixo: HEAD explícito e gerado

Na revisão Fastify `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3`, o ramo selecionado de `buildRouting.route` entra no switch de `prefixTrailingSlash` quando `path === '/' && prefix.length > 0 && !opts.isGeneratedHeadRoute`. A revisão anterior `0b076ca595d19951c536daf515c778b38cf6ba69` testava `opts.method !== 'HEAD'` como terceira condição da conjunção. Os requisitos de caminho e prefixo permanecem. Evidência: novo `lib/route.js:250–274`, antigo `:250–273`.

Assim, um HEAD explícito com marcador de geração falso deixa de ser excluído pela comparação do método nessa condição. Essa é uma afirmação sobre a condição escrita, supondo que o controle anterior a alcance; não garante registro bem-sucedido para toda entrada possível.

O marcador local vem de `opts.isGeneratedHeadRoute = isFastify === true` depois da cópia das opções (`lib/route.js:206–213`). No caminho examinado de geração de HEAD, `shouldExposeHead && isGetRoute && !isHeadRoute && !hasHEADHandler` condiciona uma chamada de `prepareRoute.call` com `method: 'HEAD'` e `isFastify: true` (`:457–459`). Depois, `prepareRoute` encaminha `isFastify` a `route.call` (`:143–170`). Esses vínculos selecionados explicam a distinção do marcador; não cobrem todos os chamadores da API.

O corpo do switch e o ramo else subsequente permanecem textualmente iguais nessa revisão. O caso `slash` passa `path`; `no-slash` passa um caminho vazio. O caso `both`/default primeiro adiciona o caminho vazio e adiciona o outro caminho somente sob `ignoreTrailingSlash !== true && (ignoreDuplicateSlashes !== true || !prefix.endsWith('/'))`. Se a condição externa do switch é falsa, o ramo seguinte pode remover uma barra inicial quando `path[0] === '/' && prefix.endsWith('/')`; caso contrário, passa `path`. Evidência: novo `lib/route.js:254–274`.

## FAQ

**Todas as rotas HEAD agora recebem tratamento idêntico?** Não. A condição selecionada distingue o marcador de geração e mantém os requisitos de caminho/prefixo e as condições posteriores dos ramos.

**O marcador de geração sozinho prova que o registro terá sucesso?** Não. A validação anterior, as chamadas posteriores e o comportamento de runtime estão fora deste resultado estático.

**Fastify ou seus testes foram executados?** Não. O parser TypeScript existente analisou o código em modo JavaScript e registrou o escopo léxico. Uma abstração booleana própria explorou as duas condições; ela não estabelece alcançabilidade ou comportamento da aplicação.

Este candidato isolado está pronto apenas para revisão do proprietário. Não é aprovado pelo proprietário, gold de treinamento, pontuação de holdout independente ou atualização operacional do catálogo.
