# Zod v4: fronteiras de parsing síncrono e assíncrono

Candidato de pesquisa isolado. Somente revisão da fonte pelo autor; verificação separada e revisão do proprietário pendentes. Sem aprovação para publicação ou treino.

colinhacks/zod @ `2a343ed2a4ffbea73fb83862ee1e317662292481`. Este capítulo cobre o contrato selecionado, não o repositório inteiro. Evidência: `source-freeze-v1.json`; critérios: `acceptance-protocol-v1.json`.

## Arquitetura e comportamento

**Z01** — O caminho síncrono _parse executa schema._zod.run com async false, lança $ZodAsyncError para um resultado Promise e lança um erro construído quando há issues. [Z01: `packages/zod/src/v4/core/parse.ts:22-39`]

**Z02** — _parseAsync define async true, aguarda um resultado Promise, lança erro quando há issues e, caso contrário, retorna o valor resultante. [Z02: `packages/zod/src/v4/core/parse.ts:48-63`]

**Z03** — _safeParse ainda lança $ZodAsyncError para um resultado Promise; safe não estabelece que toda falha vira um objeto retornado. [Z03: `packages/zod/src/v4/core/parse.ts:71-80`]

**Z04** — O objeto de falha expõe success false. Se nenhum erro já tiver sido definido, seu getter constrói e armazena error; o setter pode fornecer uma substituição, inclusive antes da primeira leitura do getter. [Z04: `packages/zod/src/v4/core/parse.ts:83-103`]

**Z05** — _safeParseAsync aguarda um resultado Promise e retorna failure(...) ou um objeto success true com data. [Z05: `packages/zod/src/v4/core/parse.ts:111-119`]

**Z06** — As exportações parse da camada classic vinculam as factories core a ZodRealError, com tipos de retorno assíncronos explícitos para parseAsync e safeParseAsync. [Z06: `packages/zod/src/v4/classic/parse.ts:8-33`]

## Exemplo

Fragmento sintético de uso, não executado. Resolva dependências em um ambiente autorizado separadamente antes de executar. Nenhum comando de inicialização ou instalação está autorizado aqui.

```typescript
import * as z from "zod/v4";
const result = await z.string().safeParseAsync("sample");
if (result.success) console.log(result.data);
```

## Evidências de testes e limitações

`packages/zod/src/v4/classic/tests/async-parsing.test.ts` está preservado como evidência de testes escritos. Nenhuma suíte externa, exemplo, instalação de dependências ou runtime foi executado. Asserções escritas não são resultados aprovados. Nenhum benchmark, garantia de concorrência ou compatibilidade de API entre releases foi estabelecido.

## FAQ

### Q001 — safeParse pode lançar uma exceção?

_safeParse ainda lança $ZodAsyncError para um resultado Promise; safe não estabelece que toda falha vira um objeto retornado. [Z03]

### Q002 — Quando o erro do objeto de falha é construído?

O objeto de falha expõe success false. Se nenhum erro já tiver sido definido, seu getter constrói e armazena error; o setter pode fornecer uma substituição, inclusive antes da primeira leitura do getter. [Z04]

### Q003 — O que distingue a fachada classic?

As exportações parse da camada classic vinculam as factories core a ZodRealError, com tipos de retorno assíncronos explícitos para parseAsync e safeParseAsync. [Z06]

## Manutenção e direitos

Este clone raso não possui o pai de HEAD localmente. Uma decisão histórica MODIFY é INCONCLUSIVE sem uma fonte anterior verificada e documentação correspondente. Símbolos ausentes neste escopo selecionado não autorizam REMOVE. A documentação existente do projeto permanece sem alterações.

MIT / LICENSE. Os avisos estão preservados com o snapshot de fonte. Este artefato é somente para avaliação, excluído de treino e não aprovado pelo proprietário.
