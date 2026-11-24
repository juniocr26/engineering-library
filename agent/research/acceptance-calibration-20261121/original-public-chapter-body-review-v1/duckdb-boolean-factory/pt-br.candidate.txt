# Factory booleana e construtor têm papéis diferentes

Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.

Repository: duckdb; revision: e41515de6f7efb19b43293ab49cb967cd64ab9f9; baseline: duckdb-boolean-factory. [Exact source excerpts](source-excerpts.json).

## Leia a declaração antes de nomear o papel

O baseline real do agente local chamou `Value::BOOLEAN` de construtor. A definição selecionada começa, porém, com `Value Value::BOOLEAN(bool value)`: possui tipo explícito de resultado `Value` e um return explícito de um resultado local. Esses detalhes identificam uma função factory na evidência selecionada. Um construtor tem outra forma de declaração. A distinção importa porque confundir os dois esconde a sequência de inicialização seguida de mutação.

O pacote de fonte inclui o construtor `Value(LogicalType)` e a factory booleana como trechos separados do mesmo arquivo fixado. O pacote selecionado original não estabelecia que a factory fosse estática apenas pela definição fora da classe. Esta campanha acrescenta o cabeçalho de declaração correspondente, que declara explicitamente a factory como estática. Também não afirma interpretação ou avaliação de consulta SQL: nenhuma aplicação DuckDB foi compilada ou executada aqui.

## O construtor estabelece um estado intermediário

O construtor selecionado é `Value::Value(LogicalType type)`. Sua lista de inicialização inicializa `type_` com `std::move(type)` e `is_null` com true. Isso registra a inicialização escrita desses membros. Não mostra toda invariante da representação de `Value` nem estabelece que todo construtor da classe inicialize um conteúdo booleano. Sobrecargas próximas possuem corpos próprios e não devem ser fundidas silenciosamente a esta.

A factory inicia seu resultado local com `Value result(LogicalType::BOOLEAN)`. Sob o contrato do construtor mostrado, o tipo lógico solicitado e a flag nula inicial são partes distintas do estado. A flag nula verdadeira na construção é um estado intermediário na execução desta factory. Relatá-la como resultado final da factory interromperia o percurso antes das duas atribuições seguintes.

## Conteúdo, flag nula e objeto retornado

A instrução seguinte é `result.value_.boolean = value`. Ela armazena o bool recebido no membro booleano do conteúdo do objeto local. A instrução posterior define `result.is_null = false`. A fonte escreve, portanto, o conteúdo e o marcador nulo separadamente. Não deriva o marcador nulo de a entrada ser verdadeira ou falsa: ambas as entradas bool comuns alcançam a mesma atribuição de marcador falso.

A última instrução é `return result`. O resultado declarado é um objeto `Value`, em vez de bool isolado, ponteiro ou marcador nulo intermediário. O código selecionado não demonstra conversão dinâmica de string, inteiro ou expressão SQL arbitrária. Qualquer conversão anterior ao fornecimento do parâmetro bool pertence a outra evidência. Também seria incorreto interpretar o marcador nulo falso do objeto retornado como conteúdo booleano falso.

## Uma correção com escopo deliberadamente restrito

Para uma entrada verdadeira conceitual, a atribuição de conteúdo armazena verdadeiro e a atribuição do marcador nulo armazena falso. Para uma entrada falsa conceitual, o conteúdo se torna falso enquanto o marcador nulo novamente se torna falso. Esses são percursos derivados da fonte, não testes observados em execução. Explicam por que valor e nulidade precisam de frases separadas em um contrato útil.

Nenhum comportamento de otimizador, custo de alocação, garantia de exceção ou desempenho de elisão de cópia foi medido. A evidência sustenta a sequência escrita nesses trechos, não uma descrição universal dos valores DuckDB. As observações corretas do baseline sobre armazenar a entrada e mudar a nulidade são mantidas, enquanto seu erro de papel da declaração é corrigido. Os capítulos bilíngues continuam candidatos revisados contra a fonte e pendentes de aprovação do proprietário; nenhum se torna gold de treinamento apenas porque sua estrutura e paridade de trechos de código foram verificadas.

## FAQ de engenharia e limite da declaração

<!-- reading-section: faq:static-factory-identity -->
### BOOLEAN é construtor ou factory estática?

O cabeçalho público acrescentado declara `DUCKDB_API static Value BOOLEAN(bool value);`. Isso estabelece a declaração de factory estática na revisão congelada. O construtor é declarado separadamente com argumento de tipo lógico. Definição e declaração agora sustentam papéis distintos sem adivinhar pelo nome em maiúsculas.

<!-- reading-section: faq:false-versus-null -->
### Um conteúdo falso significa SQL null?

O conteúdo e a flag de nulidade são membros escritos distintos. Os dois caminhos comuns de entrada bool atribuem `result.is_null = false`. Um conteúdo falso, portanto, não transforma essa atribuição em resultado nulo.

<!-- reading-section: faq:no-query-pipeline-proof -->
### Essa fonte demonstra um pipeline de consulta ou conversão?

Mostra construção, duas atribuições e retorno de um Value local. Não interpreta SQL, executa instrução de banco ou prova garantias de conversão, alocação, desempenho ou exceção para entradas arbitrárias.

| Entrada bool conceitual | Atribuição escrita ao conteúdo | Flag nula final escrita |
| --- | --- | --- |
| true | true | false |
| false | false | false |

Essas linhas da tabela são percursos derivados da fonte, não execuções observadas do DuckDB. O cabeçalho adicional de tipos declara o identificador lógico booleano e o construtor de conversão de tipo lógico; verificação completa de build e sobrecargas permanece fora desta revisão.
