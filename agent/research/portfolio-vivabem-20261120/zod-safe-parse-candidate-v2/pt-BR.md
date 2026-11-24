# Safe parsing no core do Zod: ramos de resultado e erros sob demanda

Este capítulo cobre seis grupos selecionados do código de `colinhacks/zod` em `2a343ed2a4ffbea73fb83862ee1e317662292481`: preparação síncrona e lançamento explícito sob a condição de Promise, escolha do resultado, getter da falha, setter da falha, equivalente assíncrono e vínculos das factories do core. Descreve a implementação escrita em `packages/zod/src/v4/core/parse.ts`, não toda a API do Zod ou comportamento observado em runtime. O repositório fixado tem licença MIT; isso não fornece aprovação do proprietário para treinamento ou publicação deste candidato.

## Da factory ao resultado

`_safeParse` recebe `_Err` e retorna uma arrow que aceita `schema`, `value` e `_ctx`. Essa arrow cria um contexto com `async: false`, sobrescrevendo essa propriedade ao copiar um contexto fornecido. Chama `schema._zod.run({ value, issues: [] }, ctx)`. Se o resultado retornado satisfaz a condição escrita `result instanceof Promise`, a função lança `new core.$ZodAsyncError()`. Portanto, “safe” não significa que essa implementação síncrona não contém lançamentos. Evidência: `packages/zod/src/v4/core/parse.ts:71–76`.

Se o controle alcança o retorno seguinte, `result.issues.length` escolhe `failure(_Err, result.issues, ctx)`. Caso contrário, o literal retornado tem `success: true` e `data: result.value`. Esses são os ramos de retorno selecionados, não uma garantia de que todo callback de schema, acesso a propriedade ou dependência termine normalmente. Evidência: `packages/zod/src/v4/core/parse.ts:78–79`.

A constante `safeParse` do core chama `_safeParse(errors.$ZodRealError)`. Seu equivalente assíncrono chama `_safeParseAsync(errors.$ZodRealError)`. Esses são vínculos neste módulo do core; o capítulo não estabelece todo caminho de importação do pacote ou de métodos de instância. Evidência: `packages/zod/src/v4/core/parse.ts:80,119`.

## Um objeto de falha possui um accessor

`failure` declara a variável local `error` inicialmente sem inicializador e retorna um objeto com `success: false`, um getter de `error` e um setter de `error`. No getter, `if (!error)` condiciona a construção por `new Err(...)`, com as issues mapeadas por `util.finalizeIssue(iss, ctx, core.config())`. Depois que essa construção termina, o ramo atribui `undefined as any` tanto a `issues` quanto a `ctx`; em seguida, o getter retorna `error`. Evidência: `packages/zod/src/v4/core/parse.ts:83–95`.

O setter primeiro atribui seu parâmetro `e` à variável local `error` e depois limpa `issues` e `ctx`. Assim, uma substituição truthy fornecida antes de o getter executar impede que seu ramo de construção execute na leitura posterior, supondo que as operações mostradas terminem e não haja reatribuição intermediária. A condição efetiva é truthiness, não um indicador separado de “já foi lido”. A anotação TypeScript do parâmetro não é uma condição de validação em runtime. Evidência: `packages/zod/src/v4/core/parse.ts:96–101` e `:87–94`.

Não transforme isso em um contrato incondicional de que “a primeira leitura sempre constrói um erro”. Um setter pode preceder a leitura. A construção ou a finalização também pode lançar antes das atribuições seguintes que limpam as capturas. O código selecionado não certifica liberação de memória, medições de desempenho, comportamento arbitrário do chamador ou segurança universal contra exceções. A campanha não reproduziu os números de benchmark mencionados no comentário do código.

## O equivalente assíncrono

`_safeParseAsync` retorna uma arrow `async`. Cria um contexto com `async: true`, chama a mesma forma escrita de `schema._zod.run` e aguarda `result` se `result instanceof Promise`. Depois usa a escolha correspondente entre falha e sucesso por `result.issues.length`. Diferentemente da arrow síncrona selecionada, não contém aquele lançamento explícito condicionado à Promise. Isso não prova que a Promise retornada sempre seja resolvida com sucesso ou que dependências não possam rejeitar ou lançar. Evidência: `packages/zod/src/v4/core/parse.ts:111–117`.

## Um pequeno fragmento de uso

Este fragmento ilustrativo pressupõe que `safeParse`, `schema` e `input` já foram fornecidos. Mostra a escolha pelo resultado e uma leitura explícita do accessor da falha; não é um exemplo completo de importação ou construção de schema.

```typescript
const result = safeParse(schema, input);
if (result.success) {
  const data = result.data;
  void data;
} else {
  const error = result.error;
  void error;
}
```

Somente a sintaxe TypeScript é verificada para esse fragmento. A arrow retornada pela factory selecionada do core tem os dois argumentos obrigatórios mostrados aqui e um contexto opcional segundo seu tipo declarado. Resolução de módulos, verificação de tipos, dependências e comportamento em runtime não são verificados. Ler `result.error` é uma operação distinta de apenas testar `result.success`.

## Testes escritos, não observações de aprovação

O arquivo fixado `packages/zod/src/v4/classic/tests/async-parsing.test.ts:8–19` contém um teste de string que aguarda `safeParseAsync` para entradas válidas e inválidas, verifica os dois valores de `success` e inspeciona condicionalmente os dados ou uma instância de erro. O teste de número em `:23–34` escreve assertions análogas. São testes de métodos de instância em outra camada de módulo. Não foram executados e não provam de modo independente todo o vínculo com as factories selecionadas do core, o caminho do setter ou a condição síncrona de Promise.

## FAQ

**Safe parsing nunca lança?** Essa afirmação universal não tem suporte. A arrow síncrona selecionada lança explicitamente `core.$ZodAsyncError` sob sua condição de Promise; outras operações não estão envolvidas por um tratador geral de exceções aqui.

**Verificar a falha necessariamente constrói o erro?** O literal selecionado de `failure` possui um indicador de sucesso falso e um getter separado. Apenas escolher um ramo por esse indicador não é executar o corpo escrito do getter. O getter constrói somente enquanto `!error` é satisfeito, e a construção precisa terminar antes das atribuições mostradas de limpeza.

**Uma substituição pode afetar a leitura posterior do erro?** Sim, o setter escrito atribui o valor fornecido e limpa suas capturas. Uma substituição truthy pode fazer o getter retornar esse valor sem construir por `Err`; essa é uma condição descrita no código, não uma garantia sobre todo chamador sem tipos.

**A variante assíncrona garante sucesso?** Não. Sua condição selecionada de Promise aguarda em vez de executar o lançamento explícito síncrono, e seu retorno normal ainda distingue issues de sucesso. Rejeições, contratos de schema e comportamento arbitrário de callbacks não são certificados por esta revisão estática.

## Evidências e limites

Hashes exatos do código, escopos léxicos, citações físicas e seis grupos registrados de fatos estão nas evidências isoladas de pesquisa. O parser TypeScript existente lê o código como texto; não importa nem executa o Zod. Um revisor separado obtém novamente objetos públicos do Git e consulta seu AST. Controles sintéticos de admissão são verificações de desenvolvimento, não casos independentes de avaliação ou um verificador semântico geral. Este capítulo exige revisão concluída antes da aceitação baseada no código; aprovação do proprietário, gold de treinamento, integração operacional ao catálogo e publicação permanecem falsos.
