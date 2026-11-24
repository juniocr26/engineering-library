# Tratamento de barra final no prefixo: HEAD explícito e gerado

Na revisão Fastify `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3`, o ramo selecionado de `buildRouting.route` entra no switch de `prefixTrailingSlash` quando `path === '/' && prefix.length > 0 && !opts.isGeneratedHeadRoute`. A revisão anterior `0b076ca595d19951c536daf515c778b38cf6ba69` testava `opts.method !== 'HEAD'` como terceira condição da conjunção. Os requisitos de caminho e prefixo permanecem. Evidência: novo `lib/route.js:250–274`, antigo `:250–273`.

Assim, quando `opts.method` é exatamente a string `HEAD` e o marcador de geração é falso, a comparação de método que antes o excluía deixa de estar presente nessa condição. Essa é uma afirmação sobre a condição escrita, supondo que o controle anterior a alcance; não garante registro bem-sucedido para toda entrada possível.

O marcador local vem de `opts.isGeneratedHeadRoute = isFastify === true` depois da cópia das opções (`lib/route.js:206–213`). No caminho examinado de geração de HEAD, `shouldExposeHead && isGetRoute && !isHeadRoute && !hasHEADHandler` condiciona uma chamada de `prepareRoute.call` com `method: 'HEAD'` e `isFastify: true` (`:457–459`). Depois, `prepareRoute` encaminha `isFastify` a `route.call` (`:143–170`). Esses vínculos selecionados explicam a distinção do marcador; não cobrem todos os chamadores da API.

O corpo do switch e o ramo else subsequente permanecem textualmente iguais nessa revisão. O caso `slash` passa `path`; `no-slash` passa um caminho vazio. O caso `both`/default primeiro adiciona o caminho vazio e adiciona o outro caminho somente sob `ignoreTrailingSlash !== true && (ignoreDuplicateSlashes !== true || !prefix.endsWith('/'))`. Se a condição externa do switch é falsa, o ramo seguinte pode remover uma barra inicial quando `path[0] === '/' && prefix.endsWith('/')`; caso contrário, passa `path`. Evidência: novo `lib/route.js:254–274`.

Com entradas próprias `path = '/'`, `prefix = '/p'` e marcador de geração falso, a expressão anterior copiada retornou falso para `opts.method = 'HEAD'`, mas verdadeiro para `opts.method = ['HEAD']`. A expressão revisada copiada retornou verdadeiro para ambos. Um array que contém um método não é estritamente igual a essa string. O código ao redor também possui um ramo `Array.isArray(opts.method)` (`lib/route.js:231–245`); essa observação não prova normalização, registro completo ou alcançabilidade de toda combinação de entradas sintéticas.

Dezesseis avaliações das duas expressões booleanas copiadas corresponderam à referência fixada de oito casos no runtime Node/TypeScript existente. Hashes exatos do código, escopo léxico e uma lista permitida de operadores/literais/propriedades do AST foram verificados antes da avaliação. O módulo original foi analisado como texto e nunca foi importado ou executado. São observações de expressões com entradas próprias, não dezesseis testes upstream.

## FAQ

**Todas as rotas HEAD agora recebem tratamento idêntico?** Não. A condição selecionada distingue o marcador de geração e mantém os requisitos de caminho/prefixo e as condições posteriores dos ramos.

**O marcador de geração sozinho prova que o registro terá sucesso?** Não. A validação anterior, as chamadas posteriores e o comportamento de runtime estão fora deste resultado estático.

**A aplicação Fastify ou sua suíte de testes upstream foi executada?** Não. Somente as duas expressões booleanas copiadas e revisadas foram avaliadas com entradas simples próprias. Não foram realizados importação do módulo, construção, inicialização, integração, acesso a configuração/dados pelas expressões inspecionadas ou testes upstream. O observador lê evidências retidas do código e escreve recibos de pesquisa.

Este candidato isolado está pronto apenas para revisão do proprietário. Não é aprovado pelo proprietário, gold de treinamento, pontuação de holdout independente ou atualização operacional do catálogo.

Evidências adicionais: `fastify-method-shape-guard-protocol-v1.json`, `fastify-method-shape-guard-review-v1.json` e `fastify-method-shape-guard-stdout-v1.json`. O candidato anterior somente estático e a abstração booleana permanecem preservados.
