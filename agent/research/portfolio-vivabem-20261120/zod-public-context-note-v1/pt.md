# Zod: entradas de fonte, métodos de instância e parsing seguro

`colinhacks/zod` em `2a343ed2a4ffbea73fb83862ee1e317662292481`.

Candidato isolado de acompanhamento com escopo de fonte, sem aprovação do proprietário, Gold ou uso em treinamento. O capítulo anterior restrito ao núcleo permanece intacto. Dezoito arquivos públicos de fonte, manifesto, licença e testes sustentam esta nota; nenhum import do Zod, instalação de pacote, build, verificação de tipos, parse ou teste do projeto foi executado.

## Condições de exportação fazem parte do limite

A raiz do pacote mapeia `@zod/source` para `./src/index.ts`, enquanto `import` e `require` apontam para alvos JavaScript compilados. A entrada de fonte selecionada reexporta o módulo externo clássico, que reexporta schemas, erros e wrappers de parse clássicos, além de um namespace do núcleo. A entrada de fonte v4 também segue as exportações clássicas. Os dois alvos compilados selecionados da raiz estavam ausentes da árvore Git fixada; isso nada diz sobre um pacote instalado ou publicado. Condições do resolvedor e equivalência do build gerado permanecem sem verificação. [Z01–Z07]

## Wrappers clássicos e do núcleo mantêm bindings diferentes

O `safeParse` clássico chama `core._safeParse(ZodRealError)`; sua contraparte assíncrona fornece o mesmo binding clássico de erro a `core._safeParseAsync`. O módulo do núcleo exporta wrappers construídos com `errors.$ZodRealError`. Ambos os caminhos usam os factories selecionados do núcleo, mas seus bindings nomeados de construtor não devem ser confundidos silenciosamente. O membro de instância clássico encaminha seu receiver, entrada e parâmetros ao wrapper clássico. [Z08, Z11, Z21–Z23]

## Um caminho concreto de construção

A função `string` selecionada passa `ZodString` a `core._string`, cujo corpo constrói a classe fornecida após chamadas auxiliares. O construtor selecionado compõe inicialização de string do núcleo, `_ZodString` e inicialização de `ZodType`. Isso estabelece uma rota escrita de construção até a tabela de membros, não todos os tipos de schema nem o sucesso de todo auxiliar de normalização. [Z10, Z12–Z15]

## Leituras de membros podem vincular e alterar uma instância

O inicializador selecionado do construtor instala membros de traits uma vez no protótipo selecionado. `members` preserva descritores de getters, mas encaminha valores de método por `defineBound`. Com um receiver comum, seu getter vincula a função e usa `own` para guardar uma propriedade própria; esse descritor é configurável e gravável. Um receiver nulo ou indefinido retorna o método bruto. Isso explica o desenho selecionado de métodos destacados sem prometer sucesso para receivers congelados, descritores sobrescritos ou objetos arbitrários. Ler um método não é necessariamente uma consulta pura. [Z16, Z19, Z20]

O getter de `spa` lê `this?.safeParseAsync`; seu setter pode criar um valor próprio. É um alias dinâmico no caminho do getter selecionado, não garantia imutável de identidade após atribuições ou sobrescritas arbitrárias. [Z11]

## Objetos de erro e efeitos da construção

O inicializador clássico de erro delega ao inicializador do núcleo e depois define o nome clássico. O construtor de erro real fornece `Parent: Error`. O auxiliar de construtor possui ramos de pai e trait em seu `Symbol.hasInstance` personalizado; isso não é um teste de identidade nominal exata de construtor. O caminho de erro com pai chama um auxiliar que pode ajustar a configuração de stack trace ao construir o erro. Nenhum comportamento efetivo de protótipo, stack ou exceção foi medido. [Z17, Z18, Z21, Z22]

A inicialização do schema pode fornecer locale padrão pela configuração global. Um pós-processador global pode executar após inicialização e callbacks adiados. Esses hooks e a instalação de propriedades impedem uma garantia geral de pureza ou de instância inalterada. O parser síncrono selecionado do núcleo ainda possui seu throw explícito condicionado a Promise, e a falha continua usando getter/setter preguiçoso de erro; o encaminhamento público não transforma esses contratos em comportamento universal sem throw. [Z09, Z10, Z17, Z23]

## Testes escritos e reprodução

Os testes selecionados afirmam uso destacado da família de parse, substituição/restauração por spy, alias do getter e construção preguiçosa do erro. São evidência de expectativas escritas, não resultados aprovados nem certificação de todos os receivers. [Z24–Z27]

A partir da raiz do clone público, o comando somente de leitura abaixo exibe um objeto de fonte selecionado. Uma aquisição Git equivalente foi realizada; este comando não importa nem executa o módulo.

```sh
git -c core.fsmonitor=false show 2a343ed2a4ffbea73fb83862ee1e317662292481:packages/zod/src/v4/classic/parse.ts
```

## FAQ

### A exportação de fonte da raiz prova que todo import instalado segue esse caminho?

Não. A condição de fonte e os alvos compilados de import/require diferem. Nenhum build, instalação ou execução de resolvedor foi verificado. [Z01–Z07]

### Uma chamada safeParse de instância seleciona diretamente o binding de erro exportado pelo módulo do núcleo?

O membro selecionado encaminha ao wrapper clássico, que fornece o construtor clássico de erro ao factory do núcleo. Não se deve substituir esse binding pelo binding separado exportado pelo módulo do núcleo. [Z08, Z11, Z21–Z23]

### Métodos destacados são garantidos para todo objeto?

Não. A instalação selecionada vincula leituras comuns de métodos, mas descritores, formato do receiver, sobrescritas e hooks de construção importam. Os testes não foram executados. [Z16, Z19, Z20, Z24]

### spa pode continuar um alias imutável após atribuição?

Isso não foi estabelecido: seu setter selecionado sobrepõe o accessor com um valor próprio. O getter comum é um caminho diferente. [Z11]

### Parsing seguro significa que construção e leitura não têm efeitos colaterais?

Essa garantia não decorre da análise. A inicialização pode configurar padrões e chamar um pós-processador, enquanto leituras de métodos podem guardar valores próprios vinculados. O núcleo síncrono também mantém um ramo explícito de throw. [Z09, Z17, Z20, Z23]

### As asserções de teste provam correção de execução aqui?

Não. Elas foram inspecionadas sem execução. Vínculo de fonte, hashes válidos de citações, declarações de tipos, comportamento efetivo e aprovação do proprietário são estados de evidência separados. [Z24–Z27]

## Evidência e preservação

Z01–Z27 identificam intervalos físicos exatos no índice de trechos de fonte que acompanha a nota. São trechos selecionados manualmente, não declarações completas de AST nativa nem prova semântica automática. A licença MIT da raiz e os avisos dos arquivos continuam preservados. Nenhum repositório externo, capítulo existente, suíte de testes ou catálogo ativo mudou. Esta nota permanece material interno restrito de revisão, sem autorização de treinamento ou publicação.
