# Respostas TTL: sentinelas, referência temporal e unidades

Correção escrita pelo Codex e revisada contra fonte fixada; pendente de aprovação do proprietário.

Repository: redis; revision: 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb; baseline: redis-ttl-replies. [Exact source excerpts](source-excerpts.json).

## Uma resposta não é um valor de retorno C

A declaração selecionada é `void ttlGenericCommand(client *c, int output_ms, int output_abs)`. Seu tipo de resultado C é void. As chamadas a `addReplyLongLong` enviam os valores escolhidos por este corpo pelo mecanismo de resposta do cliente. O baseline real do agente local confundiu essas respostas com valores de retorno C e descreveu um ajuste de quinhentos segundos. Os dois erros apareceram em inglês e português. Esta correção separa fluxo de controle, referência temporal e unidade de saída.

Nenhum servidor Redis foi iniciado para este capítulo, e nenhum comando foi enviado pela rede. A descrição segue a fonte congelada e seus quatro wrappers imediatos. O pacote selecionado original não incluía o funcionamento interno da busca de chaves, armazenamento de expiração ou implementação do instante do comando. Esta revisão acrescenta o helper de instante abaixo e preserva os demais limites de dependência.

## Chaves ausentes saem antes da conversão

A variável local ttl começa em -1. O corpo busca `c->argv[1]` com `LOOKUP_NOTOUCH`. Se o ponteiro resultante é `NULL`, chama `addReplyLongLong(c,-2)` e executa um return sem valor. Esse caminho não prossegue para a busca de expiração ou a seleção final de unidade. O código selecionado distingue, portanto, uma chave ausente de uma chave existente sem expiração.

Para uma chave existente, `kvobjGetExpire` fornece expire. Quando expire é igual a -1, o corpo condicional é ignorado e ttl conserva a sentinela inicial. O ramo posterior de sentinela responde diretamente com -1. Ele não aplica a essa sentinela a aritmética de milissegundos para segundos. Afirmar que toda resposta passa por divisão apagaria esse ramo separado.

## As duas flags respondem a perguntas diferentes

Para uma expiração diferente da sentinela, `output_abs` seleciona o próprio expire ou `expire-commandTimeSnapshot()`. A primeira opção é a representação armazenada da expiração absoluta; a segunda subtrai o instante do comando para formar uma quantidade relativa. O corpo então limita um ttl calculado negativo a zero. Esse limite ocorre antes da seleção final da resposta e não é a sentinela de chave ausente ou sem expiração.

A outra flag, `output_ms`, escolhe entre ttl e `((ttl+500)/1000)`. O 500 somado pertence à quantidade em milissegundos antes da divisão inteira por 1000; não são quinhentos segundos acrescentados após a conversão. Para uma quantidade não negativa dentro do intervalo representável da aritmética, a expressão arredonda usando esse deslocamento. Este capítulo não afirma proteção contra overflow ou garantia universal do relógio, pois nenhuma delas é estabelecida pelo corpo selecionado.

## Os wrappers fixam as combinações de flags

Os quatro wrappers adjacentes tornam explícitas as combinações. `ttlCommand` passa (0, 0); `pttlCommand` passa (1, 0); `expiretimeCommand` passa (0, 1); `pexpiretimeCommand` passa (1, 1). Ler essas chamadas relaciona saída relativa ou absoluta e segundos ou milissegundos sem adivinhar pelo nome da função genérica. Cada wrapper delega; esses corpos não estabelecem os detalhes internos da serialização da resposta.

A observação útil do baseline sobre chaves ausentes e sem expiração é preservada. O contrato corrigido acrescenta a saída antecipada, o desvio da sentinela, as flags independentes e o limite zero. Trata-se de correção documental contra fonte fixada, não de nova inferência ou prova de aprendizado do modelo. Avisos de licença, resposta original incorreta e estado de revisão continuam separados, sem aprovação automática para treinamento ou publicação.

## Combinações dos wrappers

| Wrapper | output_ms | output_abs | Referência e unidade sem sentinela |
| --- | --- | --- | --- |
| ttlCommand | 0 | 0 | Quantidade relativa convertida em segundos |
| pttlCommand | 1 | 0 | Quantidade relativa em milissegundos |
| expiretimeCommand | 0 | 1 | Expiração absoluta convertida em segundos |
| pexpiretimeCommand | 1 | 1 | Expiração absoluta em milissegundos |

As sentinelas de chave ausente e sem expiração seguem seus ramos separados em vez dessa tabela de conversão.

## FAQ de engenharia

<!-- reading-section: faq:sentinels-before-rounding -->
### -2 e -1 são arredondados ou divididos por 1000?

Não. O caminho de chave ausente responde -2 e retorna antes da conversão da expiração. O caminho sem expiração responde -1 por seu próprio ramo de sentinela. Nenhum passa pela aritmética comum sem sentinela.

<!-- reading-section: faq:clock-snapshot-refresh -->
### commandTimeSnapshot lê um relógio novo em cada chamada?

A implementação acrescentada do helper retorna diretamente `server.cmd_time_snapshot`. O cabeçalho declara o tipo temporal em milissegundos e descreve esse campo como snapshot da execução raiz. O getter em si não contém syscall de relógio; momento completo das atualizações e garantias do relógio em execução exigem sua própria evidência.

<!-- reading-section: faq:reply-versus-key-deletion -->
### Uma resposta TTL bem-sucedida exclui a chave?

O corpo genérico selecionado realiza busca, seleção de expiração e chamadas de resposta. Não contém operação explícita de exclusão. Efeitos colaterais do helper de busca e entrega real pela rede ao cliente não são estabelecidos por esse trecho; portanto, isso não é garantia global de ausência de efeitos.
