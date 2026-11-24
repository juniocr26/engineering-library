# SQLx In: expansão de fatias, limites dos helpers e erros de divergência

Correção escrita pelo Codex e revisada contra a fonte; pendente de aprovação do proprietário.

SQLx revision 41dac167fdad5e3fd81d66cafba0951dc6823a30; actual completed baseline: sqlx-in-expansion-recovery. [Exact source evidence](source-excerpts.json).

## Os três resultados não são execução de banco

A declaração é `In(query string, args ...interface{}) (string, []interface{}, error)`. Ela prepara uma string de consulta e uma fatia de argumentos. O corpo mostrado não recebe conexão, não invoca uma instrução de banco e não prova que a consulta resultante seja SQL válido. O baseline do agente local reconheceu corretamente as formas de parâmetros e resultados, mas inventou um erro quando mais de trinta e dois argumentos são fornecidos e descreveu incorretamente a contagem de argumentos.

A resposta de recuperação concluída veio após uma interrupção de energia que deixou o primeiro pedido sem resposta preservada. Aquela tentativa original continua registrada separadamente como interrompida; seus tokens e sucesso são desconhecidos. A resposta substituta foi efetivamente recebida e retida. O writer a recusou por omitir o nome qualificado exigido `sqlx.In`, e a revisão da fonte rejeita de forma independente suas afirmações críticas sobre alocação e fluxo. Este capítulo é uma correção do Codex, não uma afirmação de que o modelo aprendeu o contrato.

## O array local é escolha de alocação, não um limite

O `stackMeta` local possui trinta e duas entradas de metadados. Quando o número de argumentos cabe, meta usa uma fatia desse array. Caso contrário, o código aloca `make([]argMeta, len(args))`. Não existe retorno de erro nesse ramo de escolha de alocação. Dizer que mais de trinta e dois argumentos são rejeitados confunde o pequeno buffer local com um limite público de cardinalidade.

A primeira passagem processa os argumentos em ordem. Para um argumento que satisfaz `driver.Valuer`, chama Value e retorna imediatamente string vazia, argumentos nulos e o erro recebido quando essa chamada relata erro. O argumento local transformado então entra na classificação de fatia. `flatArgsCount` acumula o comprimento de cada fatia expansível e um para cada argumento não fatia; não é apenas a contagem dos argumentos não fatia. Essa passagem preparatória ocorre antes da reescrita da consulta.

## Um tipo desreferenciado não é um valor desreferenciado

`asSliceForIn` primeiro rejeita uma interface nula. Obtém `reflect.ValueOf(i)`, passa o tipo desse valor para `reflectx.Deref`, exige kind de fatia e exclui o tipo exato `reflect.TypeOf([]byte{})`. O baseline omitiu a exceção de fatia de bytes e generalizou o helper como aceitando toda fatia. A comparação de tipo exato não deve ser expandida silenciosamente para uma regra não sustentada sobre todo tipo nomeado de fatia de bytes.

O helper `Deref` fornecido contém um if, não um laço: para kind de ponteiro, substitui o tipo local pelo tipo de elemento e então alcança o único return final. Não remove repetidamente profundidade arbitrária de ponteiros. Também não modifica o `reflect.Value` mantido por `asSliceForIn`. Esse helper retorna o valor original. Portanto, uma descrição não deve prometer tratamento transparente de valores ponteiro para fatia apenas porque um tipo foi desreferenciado. O corpo chamador de In posteriormente usa o método Len do valor retornado; o comportamento completo em execução dessas entradas não foi testado aqui.

## Fatias vazias e o caminho sem fatias vêm antes da varredura

Para uma fatia classificada como expansível, In registra seu comprimento e rejeita comprimento zero com string vazia, argumentos nulos e o erro de fatia vazia. Isso ocorre na primeira passagem, antes de procurar pontos de interrogação na consulta. Não depende de alcançar depois um placeholder correspondente. Uma fatia vazia de bytes do tipo exato segue a exclusão de fatia de bytes do helper, em vez desse ramo de fatia expansível.

Se nenhuma fatia expansível foi encontrada, o caminho rápido retorna `query, args, nil`. Esses são a fatia de argumentos original e a consulta original. O laço preparatório anterior já executou, portanto isso não significa que nenhum Valuer foi chamado. Também significa que as verificações posteriores da contagem de placeholders são ignoradas nesse caminho. Uma afirmação genérica de que toda invocação verifica as contagens de argumentos e placeholders estaria errada.

## O caminho de reescrita preserva a ordem dos argumentos

Com pelo menos uma fatia expansível, o corpo cria `newArgs` e um construtor de string, e então procura o byte de ponto de interrogação em sufixos sucessivos da consulta. Uma entrada escalar de metadados acrescenta seu valor armazenado e avança o deslocamento. Uma entrada de fatia escreve o prefixo até aquele placeholder, acrescenta pontos de interrogação separados por vírgula para os elementos adicionais e delega o acréscimo dos elementos a `appendReflectSlice`. O sufixo restante da consulta então é processado na mesma ordem de argumentos.

A evidência de `appendReflectSlice` expandida manualmente trata fatias de interface com append variádico, fatias de inteiros e strings com laços ordenados e os outros casos com reflexão indexada. O baseline selecionado não recebeu o corpo desse helper, portanto esses detalhes são evidência da correção, em vez de descobertas do modelo. A busca de ponto de interrogação mostrada aqui não é um lexer SQL que exclui strings entre aspas ou comentários; nenhum estado desse tipo de interpretação aparece nas funções selecionadas.

## Erros de divergência são distintos da tupla de sucesso

Durante a reescrita, encontrar outro placeholder depois de consumir todas as entradas de metadados retorna string vazia, argumentos nulos e o erro de mais variáveis de associação. Após a varredura, entradas de metadados não usadas produzem o erro de menos variáveis de associação, com a mesma forma de resultado string vazia e argumentos nulos. Esses são ramos escritos separados. Não retornam o prefixo `newArgs` parcialmente acumulado como `bindMapArgs` faz em seu contrato diferente de nome ausente.

A instrução final de sucesso retorna `buf.String(), newArgs, nil`. Descrever esse último resultado apenas como “um erro” perde o valor nulo de sucesso escrito explicitamente. Todo o contrato corrigido continua condicionado à conclusão comum dos helpers invocados e das operações de reflexão. Nenhuma aplicação SQLx ou banco foi executado, e nenhum peso do modelo mudou. Fonte exata, avisos de licença retidos e paridade bilíngue de trechos de código apoiam a revisão; aprovação do proprietário e direitos de treinamento continuam sendo gates separados.

## FAQ de engenharia

<!-- reading-section: faq:metadata-array-not-argument-cap -->
### Mais de 32 argumentos são rejeitados?

Não há essa rejeição escrita no ramo de alocação. Uma entrada maior aloca metadados do tamanho da contagem de argumentos. Conclusão normal da alocação e dos helpers continua sendo premissa; o tamanho do buffer local não é o limite público afirmado pelo baseline histórico.

<!-- reading-section: faq:valuer-before-no-slice-fast-path -->
### O caminho sem fatias pula todos os helpers e valida a contagem de placeholders?

O laço preparatório já executou, incluindo qualquer chamada aplicável a Valuer. Quando não encontra fatia expansível, a função retorna a consulta e a fatia de argumentos originais antes das verificações de divergência da reescrita. Não substitui todos os valores locais transformados nessa fatia original.

<!-- reading-section: faq:byte-scan-not-sql-parser -->
### A busca de pontos de interrogação entende aspas e comentários SQL?

A implementação selecionada procura bytes com `strings.IndexByte`; não mostra estado de aspas ou comentários SQL. Da mesma forma, a exclusão do tipo exato de fatia de bytes não deve ser generalizada a todo tipo de fatia definido separadamente sem sua própria evidência. O resultado ainda exige tratamento posterior apropriado de placeholders e execução de banco em outro componente.
