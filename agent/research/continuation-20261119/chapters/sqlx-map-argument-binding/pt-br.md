# Associação de argumentos de mapa: presença, ordem e prefixo retornado no erro

Correção escrita pelo Codex e revisada contra a fonte; pendente de aprovação do proprietário. SQLx na revisão 41dac167fdad5e3fd81d66cafba0951dc6823a30, named.go. Baseline real do agente local: sqlx-bind-map. Evidência exata: [trecho da fonte](source-excerpts.json). Nenhuma aplicação SQLx foi compilada ou executada.

## As duas entradas têm papéis diferentes

A declaração `bindMapArgs(names []string, arg map[string]interface{}) ([]interface{}, error)` recebe uma fatia ordenada de nomes e um mapa dos valores correspondentes. Constrói uma fatia de argumentos posicionais. O corpo selecionado não recebe string de consulta, conexão ou transação. Seu comportamento não deve ser confundido com interpretar placeholders nomeados, reescrever SQL ou executar uma operação de banco em outro ponto do pacote.

O baseline real do agente local reconheceu a busca no mapa e a acumulação em alto nível. Não descreveu completamente o prefixo acumulado retornado no erro, a flag de presença quando um valor é nulo, nomes repetidos ou entrada vazia. Esta correção preserva essas observações válidas e explicita os casos ausentes. A fonte está congelada; os exemplos abaixo são consequências derivadas da fonte sob a semântica comum de mapas e fatias Go, não execuções observadas de banco.

## A alocação começa sem valores acumulados

A primeira instrução inicializa `arglist` com `make([]interface{}, 0, len(names))`. O argumento de comprimento é zero; `len(names)` fornece a capacidade inicial. Isso não preenche o resultado com um valor zero para cada nome. Os valores entram no resultado apenas pela instrução posterior de append. Descrevê-lo como array de resultado com tamanho fixo perderia, portanto, tanto o tipo fatia quanto seu comprimento crescente.

O laço percorre names. Não percorre o mapa nem ordena os nomes fornecidos. Assim, a ordem posicional segue a sequência de nomes recebida no caminho comum de sucesso. Isso importa quando um chamador espera que a ordem dos placeholders corresponda aos valores resultantes, mas a função selecionada não verifica cardinalidade de placeholders ou texto de consulta.

## A presença é verificada separadamente do valor armazenado

Cada iteração executa `val, ok := arg[name]`. Sua guarda é `!ok`. Não testa se `val` é nulo, zero, falso ou string vazia. Uma chave existente com valor de interface nulo segue, portanto, o mesmo caminho de append de qualquer outro valor presente. Ausência e presença com valor nulo são casos distintos. Substituir o teste de presença por um teste de valor mudaria esse contrato.

Na semântica comum de mapas Go, ler um mapa nulo também é diferente de escrever nele. Para um nome solicitado, a busca não encontra chave correspondente e alcança o caminho de nome ausente; este corpo não atribui valores ao mapa. names vazio não produz busca alguma. Essas observações descrevem o caminho mostrado e não prometem ausência de toda falha possível de execução ou de mutação concorrente.

## O primeiro nome ausente retorna o prefixo existente

O ramo de nome ausente retorna `arglist` junto de `fmt.Errorf("could not find name %s in %#v", name, arg)`. A fatia já acumulada é preservada nesse retorno escrito. O corpo não a limpa nem a substitui por uma fatia nula antes de retornar. Se a expressão de erro conclui normalmente, esse return encerra a função antes de processar os nomes posteriores.

Por exemplo, considere names contendo a, missing e b nessa ordem, com valores disponíveis apenas para a e b. Depois de acrescentar o valor de a, a segunda busca alcança o ramo de erro. A fatia retornada contém aquele primeiro valor; o valor posterior de b não é acrescentado por essa invocação. Um resumo que diz apenas “retorna erro quando falta uma chave” omite uma parte relevante do contrato de dois resultados.

## Repetições e entrada vazia são casos preservados

Quando a chave está presente, o corpo acrescenta `val` e prossegue. Não contém conjunto de deduplicação, remoção do mapa ou marcador de consumo. Nomes repetidos podem, portanto, acrescentar o mesmo valor mapeado repetidamente. O resultado não tem garantia de valores exclusivos apenas porque um mapa é usado para busca. Acrescentar valores de interface também não demonstra cópia profunda dos objetos referenciados.

Após o laço, a instrução final escrita é `return arglist, nil`. Sem nomes, o corpo do laço é ignorado e a fatia alocada inicialmente vazia alcança esse retorno. O resultado comum concluído da função tem um valor acrescentado por nome processado com sucesso, incluindo repetições. Tratamento do erro pelo chamador, execução posterior de SQL, propriedade dos objetos e segurança entre threads continuam sendo contratos separados. O capítulo corrigido aguarda revisão do proprietário, sem aprovação automática para treinamento ou afirmação de que o modelo local aprendeu essas distinções.

