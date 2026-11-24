# Totalist: percurso no código e limites do pacote

Candidato isolado de capítulo revisado a partir do código. Revisão `4b071d3e54d466a4059de89006c752da782c8b02` (`3.0.1`); sem publicação ou aprovação para treinamento. As afirmações abaixo se referem ao recorte preservado, em vez de um pacote instalado.

## Propósito e responsabilidades

**C1** O manifesto fixado nomeia `totalist` versão `3.0.1`; seu campo `modes` mapeia `default` para `src/async.js` e `sync` para `src/sync.js`. [T1]

**C2** Ambos os módulos selecionados declaram a exportação nomeada `totalist(dir, callback, pre='')`; a declaração assíncrona tem o modificador `async` e a declaração síncrona não tem. [T2] [T3]

**C3** Ambos os corpos atribuem `dir = resolve('.', dir)`, obtêm entradas do diretório, formam `abs` com `join` e usam `stats.isDirectory()` para escolher entre recursão e chamada do callback. A expressão de callback recebe o nome relativo unido, `abs` e `stats`. [T2] [T3]

**C4** O código assíncrono envolve `stat` e `readdir` com `promisify`, usa `arr.map` e fornece os resultados a `Promise.all`. Seu callback interno retorna a chamada recursiva ou a expressão de callback do usuário. [T2]

**C5** O código síncrono chama `readdirSync` e `statSync` em um laço indexado. Sua expressão de callback é uma instrução, em vez de um valor retornado ou aguardado; a função selecionada não tem instrução de retorno escrita. [T3]

**C6** As declarações de código tipam `Caller` como `(relPath: string, absPath: string, stats: Stats) => any`. A anotação de retorno assíncrona é `Promise<void>` e a síncrona é `void`; ambas as declarações chamam o terceiro argumento opcional de `prefix`, enquanto a implementação o chama de `pre`. [T4] [T5]

**C7** O manifesto exporta `.` e `./sync`, cada um com destinos `types`, `import` e `require`. Esses destinos apontam para caminhos de distribuição gerados, em vez de apontarem diretamente para os dois arquivos JavaScript selecionados. [T1]

**C8** O manifesto declara `engines.node` como `>=6`, enquanto o README fixado identifica o modo assíncrono como `>= 8.x` e o síncrono como `>= 6.x`. Este recorte não justifica uma única versão mínima testada do Node para ambos os modos. [T1] [T6]

**C9** Os corpos selecionados não contêm cláusula de captura escrita, ordenação explícita, limite de profundidade de percurso, limitador de concorrência ou registro explícito de ciclos. Esta é uma inspeção delimitada do código, sem garantir o comportamento do sistema de arquivos importado ou todos os erros possíveis em execução. [T2] [T3]

**C10** A licença preservada é MIT. A presença da licença por si só não aprova um futuro alvo de treinamento, e este capítulo permanece excluído do treinamento. [T7]

## Arquitetura e tabela de dependências

| Camada | Dependência ou destino escrito | Evidência |
|---|---|---|
| async | `path`, `fs`, `util.promisify`, `Promise.all` | [T2] |
| sync | `path`, `fs`, `readdirSync`, `statSync` | [T3] |
| types | `Stats` from `fs`, `Caller`, `prefix` | [T4] [T5] |
| package | `.`, `./sync`, `types`, `import`, `require` | [T1] |

## Exemplo e comando ilustrativos

O exemplo permite verificação de sintaxe e não foi executado. Seu destino de importação não foi autenticado por este estudo. Nenhuma lista esperada de arquivos é inventada.

```js
import { totalist } from 'totalist';
const relativePaths = [];
await totalist('src', (relativePath, absolutePath, stats) => {
  relativePaths.push(relativePath);
});
// Illustrative only: no particular result set or order is asserted.
```

```sh
node --check totalist-example.mjs
```

## Perguntas frequentes

### Q1 — Este recorte pode certificar o pacote publicado?

Não. A árvore Git completa e fixada não contém arquivos de distribuição em `dist/` ou `sync/`, e nenhum arquivo de pacote de registro foi autenticado nem build executado. Destinos do manifesto e declarações de código são camadas distintas de evidência.

### Q2 — O callback prova que cada entrada é um arquivo regular?

Não. A condição escrita testa `stats.isDirectory()` e, no outro ramo, chama o callback; ela não testa `stats.isFile()`. Comportamento de links simbólicos, disputas de acesso e segurança contra ciclos não foram exercitados.

### Q3 — O modo síncrono aguarda uma Promise retornada pelo callback?

O corpo síncrono não contém `await` e não retorna nem inspeciona o valor do callback. A declaração ainda aceita um `Caller` que retorna `any`; ela não fornece garantia estática de conclusão de callback assíncrono.

### Q4 — Qual versão mínima do Node a documentação deve informar?

Informe a divergência explicitamente: manifesto `>=6`, README assíncrono `>= 8.x`, README síncrono `>= 6.x`. Nenhuma execução de compatibilidade entre versões foi realizada.

### Q5 — Ordem de saída e paralelismo limitado estão garantidos?

Não. O código assíncrono usa `arr.map` com `Promise.all`; nenhum corpo selecionado ordena explicitamente nem implementa um limitador de concorrência. Esta observação não estabelece escalonamento em execução nem ordenação do sistema de arquivos.

### Q6 — Nomes de parâmetros inalterados justificam NO-OP do pacote inteiro?

Não. O código anterior usava uma exportação padrão chamada `list`; esta revisão usa a exportação nomeada `totalist`. Os metadados do pacote também acrescentam um mapa `exports`. Uma observação apenas da assinatura não pode certificar exemplos de importação inalterados nem o capítulo inteiro.

## Limites da verificação

Não houve instalação do pacote, build, percurso de diretórios, observação de links simbólicos, execução de callback, execução de dependências importadas, matriz de compatibilidade em execução, publicação ou revisão do proprietário. A verificação de sintaxe do exemplo não certifica resolução de importações nem comportamento do sistema de arquivos.

## Citações de código

[T1]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/package.json#L1 "0623891e622ac83bd53ef5a81987338da75697112e2386ffbd77676c1ef7e9df"

[T2]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/async.js#L1 "70a998ce6b3da13e242332e704d9b64ee88c23520ee260663d178206a57ae14d"

[T3]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/sync.js#L1 "0d911e865ba4c7e860a1ebb8e6fd7b25e5113967bea3e799bca690c48fdd41c0"

[T4]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/async.d.ts#L1 "9f78bd6e43202253f0af72af9978cda3399b5a1ae9cd28593976f42cf6a1f4ee"

[T5]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/sync.d.ts#L1 "4cdaa2f28b917cc3fb61454657fed974968a66557ef23c2858997565d3b9559c"

[T6]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/readme.md#L1 "fb37c2d537fe6d81bb653a447a192348f373577be88f2a1aa66696e751c6bf7d"

[T7]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/license#L1 "306fa513e39b23a6e8747520de761809d206b99800ef41907b530226574c59ae"
