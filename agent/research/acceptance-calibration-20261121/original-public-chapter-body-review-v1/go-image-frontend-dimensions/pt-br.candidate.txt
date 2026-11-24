# Dimensões de redimensionamento no frontend: cálculo e mensagens são separados

Correção experimental revisada na fonte pelo Codex, pendente de aprovação humana. Fonte congelada: go-image-optimizer na revisão `48476de6e4450294b7769ab7af90805100bb21b5`, `frontend/app/components/image-resize/resize-options.ts`. O baseline real do modelo local é `go-image-optimizer-dimensionerror`. Seu pacote continha somente `dimensionError`; esta correção acrescenta explicitamente `targetDimensions` e as declarações de tipos do mesmo arquivo. Nenhum navegador, aplicação externa ou operação de imagem foi executado.

## Os papéis dos dados na fronteira da função

O tipo `ImageInfo` descreve campos da imagem original, incluindo dimensões e quantidade de quadros. O tipo `ResizeOptions` descreve modo, strings de dimensões, eixo selecionado, redução numérica e opção de preservar proporção. Essas declarações descrevem formatos de dados pretendidos. Não acrescentam verificações em execução aos corpos mostrados nem provam que todo chamador forneça objetos válidos.

A função `targetDimensions` recebe esses dois objetos e calcula um resultado candidato. Inicialmente atribui `Number(options.width)` e `Number(options.height)` a variáveis locais. Essa conversão ocorre antes de decidir se a guarda do modo em pixels se aplica. Portanto, ler as duas strings é diferente de decidir se os valores convertidos ultrapassam a condição posterior. Não há decodificador de imagem nem requisição de rede nesta função.

## A validação do modo em pixels tem escopo explícito

A primeira guarda de retorno depende de `options.mode === "pixels"`. Nesse modo, ela chama o predicado de inteiro seguro sobre os dois valores locais e compara cada um com os limites inferior e superior. A falha em qualquer condição de dimensão listada retorna `null`. O limite superior usado para cada dimensão informada é 32 milhões; não é a mesma verificação do orçamento posterior de produto.

As duas dimensões informadas são examinadas pela guarda mesmo quando o cálculo posterior de proporção derivará uma a partir da outra. A fonte não move a validação para dentro do ramo de eixo selecionado. Por outro lado, essa guarda não se aplica apenas porque existe um valor de redução: sua comparação externa de modo importa. Uma descrição que a trate como validação universal de todos os modos perde uma condição do fluxo de controle.

## O escalonamento ocorre depois da guarda inicial

O bloco de escala é selecionado por `options.mode === "percentage" || options.keepAspectRatio`. Ele começa com `(100 - options.reduction) / 100`. Quando o modo é pixels, substitui essa escala pela altura informada dividida pela altura original ou pela largura informada dividida pela largura original, conforme o eixo selecionado. As duas dimensões de saída são calculadas a partir das dimensões originais, arredondadas e passadas por uma expressão de mínimo igual a um.

Por fim, a função retorna `{ width, height }`. O corpo não contém uma verificação separada de faixa para a redução nem uma validação completa do objeto de informações da imagem original. A presença de arredondamento e de uma expressão de mínimo não estabelece que toda entrada arbitrária em execução produza tamanho finito e válido. Este capítulo registra cálculo e guardas, sem prometer redimensionamento bem-sucedido ou aplicação dos limites pelo servidor.

## A função de mensagens não repete essas verificações

A função `dimensionError` recebe informações da imagem e um candidato anotado com `ReturnType<typeof targetDimensions>`. Sua primeira condição é `!target`, que retorna a mensagem sobre informar números inteiros positivos. Essa mensagem descreve uma orientação ao usuário. A condição verifica o valor lógico falso do candidato; não examina a positividade ou integralidade de cada dimensão.

A guarda seguinte compara `target.width * target.height > 32_000_000`. Seu ramo verdadeiro retorna a mensagem de limite de saída estática. A próxima guarda compara `target.width * target.height * info.frameCount > 64_000_000`, retornando a mensagem de limite de trabalho da animação. As duas comparações são estritas. A igualdade não satisfaz a condição correspondente de maior que, e a verificação estática ocorre antes da verificação agregada por quadros.

Se nenhuma dessas guardas retorna, o resultado final é `null`. A função mostrada retorna strings ou esse valor final; ela não lança a mensagem como exceção. Também não converte strings de dimensões nem chama a função de cálculo. A anotação expressa uma relação de tipos, enquanto o corpo efetivo continua sendo as três guardas ordenadas e o retorno final.

## O que mudou nesta correção

O baseline neural reconheceu os dois limites numéricos e o null final, mas atribuiu validação de inteiros positivos diretamente à função de mensagens. O produtor sintático independente agora acrescenta um pacote opcional que preserva as três condições e suas expressões exatas de retorno, mantendo inalterado o parágrafo anterior da primeira guarda. Isso é evidência determinística da fonte, não melhoria de pesos nem um novo gravador JavaScript de produção. O capítulo ampliado separa cálculo, validação específica de modo e apresentação de erros. A fonte, a revisão bilíngue e o estado de aprovação continuam explícitos; nenhuma saída foi publicada ou promovida a dado de treinamento aprovado.

## FAQ de engenharia

<!-- reading-section: faq:error-message-versus-validation -->
### O próprio dimensionError converte e valida as duas strings informadas?

Ele recebe um candidato e primeiro verifica seu valor lógico falso. A mensagem de números inteiros positivos não é um algoritmo separado de validação de dimensões. Conversão de strings e guarda de inteiro seguro no modo em pixels pertencem à função de cálculo.

<!-- reading-section: faq:aspect-ratio-validation-order -->
### O modo de proporção pode ignorar uma dimensão informada inválida antes da validação?

No modo em pixels, as duas dimensões informadas passam pela guarda inicial antes do cálculo posterior de escala por eixo. Essa ordem continua relevante mesmo quando uma dimensão final será derivada da outra.

<!-- reading-section: faq:pixel-boundary-and-message-return -->
### Limites de pixels iguais são rejeitados ou mensagens são lançadas como exceções?

As duas verificações de produto usam estritamente maior que. Igualdade isolada não segue esses ramos. A função retorna suas strings de mensagem ou null; não aparece throw neste corpo selecionado. Validade completa das entradas em execução e aplicação dos limites no backend exigem evidências separadas.

O [validador de dimensões do backend](../go-image-dimensions/pt-br.md) e o [validador de animação](../go-image-animation/pt-br.md) são contratos separados. Números de limite correspondentes não provam aritmética idêntica, ordem de validação ou integração completa do frontend ao servidor.
