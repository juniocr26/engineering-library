# Factory booleana e construtor têm papéis diferentes

Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.

Repository: duckdb; revision: e41515de6f7efb19b43293ab49cb967cd64ab9f9; baseline: duckdb-boolean-factory. [Exact source excerpts](source-excerpts.json).

## Leia a declaração antes de nomear o papel

O baseline real do agente local chamou `Value::BOOLEAN` de construtor. A definição selecionada começa, porém, com `Value Value::BOOLEAN(bool value)`: possui tipo explícito de resultado `Value` e um return explícito de um resultado local. Esses detalhes identificam uma função factory na evidência selecionada. Um construtor tem outra forma de declaração. A distinção importa porque confundir os dois esconde a sequência de inicialização seguida de mutação.

O pacote de fonte inclui o construtor de LogicalType e a factory booleana como trechos separados do mesmo arquivo fixado. O capítulo não infere que a factory seja estática apenas pela definição fora da classe. Nenhum cabeçalho de declaração foi acrescentado à evidência para essa afirmação. Também não afirma interpretação ou avaliação de consulta SQL: nenhuma aplicação DuckDB foi compilada ou executada aqui.

## O construtor estabelece um estado intermediário

O construtor selecionado é `Value::Value(LogicalType type)`. Sua lista de inicialização inicializa `type_` com `std::move(type)` e `is_null` com true. Isso registra a inicialização escrita desses membros. Não mostra toda invariante da representação de `Value` nem estabelece que todo construtor da classe inicialize um conteúdo booleano. Sobrecargas próximas possuem corpos próprios e não devem ser fundidas silenciosamente a esta.

A factory inicia seu resultado local com `Value result(LogicalType::BOOLEAN)`. Sob o contrato do construtor mostrado, o tipo lógico solicitado e a flag nula inicial são partes distintas do estado. A flag nula verdadeira na construção é um estado intermediário na execução desta factory. Relatá-la como resultado final da factory interromperia o percurso antes das duas atribuições seguintes.

## Conteúdo, flag nula e objeto retornado

A instrução seguinte é `result.value_.boolean = value`. Ela armazena o bool recebido no membro booleano do conteúdo do objeto local. A instrução posterior define `result.is_null = false`. A fonte escreve, portanto, o conteúdo e o marcador nulo separadamente. Não deriva o marcador nulo de a entrada ser verdadeira ou falsa: ambas as entradas bool comuns alcançam a mesma atribuição de marcador falso.

A última instrução é `return result`. O resultado declarado é um objeto `Value`, em vez de bool isolado, ponteiro ou marcador nulo intermediário. O código selecionado não demonstra conversão dinâmica de string, inteiro ou expressão SQL arbitrária. Qualquer conversão anterior ao fornecimento do parâmetro bool pertence a outra evidência. Também seria incorreto interpretar o marcador nulo falso do objeto retornado como conteúdo booleano falso.

## Uma correção com escopo deliberadamente restrito

Para uma entrada verdadeira conceitual, a atribuição de conteúdo armazena verdadeiro e a atribuição do marcador nulo armazena falso. Para uma entrada falsa conceitual, o conteúdo se torna falso enquanto o marcador nulo novamente se torna falso. Esses são percursos derivados da fonte, não testes observados em execução. Explicam por que valor e nulidade precisam de frases separadas em um contrato útil.

Nenhum comportamento de otimizador, custo de alocação, garantia de exceção ou desempenho de elisão de cópia foi medido. A evidência sustenta a sequência escrita nesses trechos, não uma descrição universal dos valores DuckDB. As observações corretas do baseline sobre armazenar a entrada e mudar a nulidade são mantidas, enquanto seu erro de papel da declaração é corrigido. Os capítulos bilíngues continuam candidatos revisados contra a fonte e pendentes de aprovação do proprietário; nenhum se torna gold de treinamento apenas porque sua estrutura e paridade de trechos de código foram verificadas.

