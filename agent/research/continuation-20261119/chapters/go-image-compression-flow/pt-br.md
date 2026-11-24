# Caso de uso de compressão: erros, verificações de contexto e delegação

Capítulo experimental revisado na fonte e escrito pelo Codex, pendente de aprovação humana. Revisão congelada: go-image-optimizer `48476de6e4450294b7769ab7af90805100bb21b5`. Os arquivos relevantes são `backend/internal/application/imagecompression/usecase.go` e `backend/internal/infrastructure/imaging/compress/compressor.go`. Os braços reais do agente, `gio-compression-flow-caller` e `gio-compression-flow-helpers`, foram preservados; ambos foram recusados por explicação insuficiente sobre as declarações específicas. Nenhum código da aplicação externa foi executado.

## A construção armazena uma dependência injetada

A aplicação declara uma interface `Compressor` com um método que recebe bytes de imagem e retorna um resultado acompanhado de um erro. Sua struct `UseCase` armazena um valor dessa interface em um campo não exportado. O construtor `NewUseCase` retorna um valor contendo a dependência fornecida. Não escolhe um codificador concreto, não chama a compressão e não examina uma imagem durante a construção.

Essa fronteira limita as conexões que uma explicação baseada apenas na fonte pode estabelecer. Outro pacote define um tipo concreto com um método compatível, mas dois nomes de método iguais não estabelecem o objeto efetivamente injetado em execução. Os arquivos fornecidos mostram uma relação estrutural possível, não a montagem da aplicação. Outra implementação, um substituto de teste ou uma dependência inválida podem ser fornecidos por outro código. Por isso, este capítulo documenta separadamente o método da aplicação e o método concreto.

## Execute verifica a entrada antes de consultar o contexto

A declaração `UseCase.Execute(ctx context.Context, input []byte) (Result, error)` recebe um contexto e os bytes da imagem. Sua primeira guarda é `len(input) == 0`. Esse ramo retorna `Result{}, ErrEmptyImage` imediatamente. Ele ocorre antes das duas verificações de contexto e da chamada ao compressor armazenado. Reordenar essas guardas na explicação pode mudar qual erro aparece quando várias precondições falham.

Para uma entrada não vazia, o método chama `ctx.Err()` e retorna um resultado zero com esse erro quando ele é diferente de nil. Não há guarda explícita de contexto nil neste corpo. Ultrapassar a primeira verificação leva a `u.compressor.Compress(input)`. O contexto não é argumento dessa chamada de interface. O corpo não estabelece que a compressão possa ser interrompida pela metade, não inicia uma tarefa em segundo plano e não impõe um temporizador separado à operação.

## Três resultados posteriores preservam os papéis de valor e erro

Se a compressão retorna um erro diferente de nil, o método retorna `Result{}, err`. Um resultado devolvido junto com esse erro é descartado nessa fronteira da aplicação. Se a compressão informa sucesso, o corpo verifica o contexto novamente. Um erro na segunda consulta ao contexto também substitui o resultado calculado por um resultado zero e retorna o erro de contexto. Somente após as duas verificações sem erro e a compressão bem-sucedida o método retorna `result, nil`.

Portanto, a segunda verificação é observável mesmo sem passar o contexto ao método da interface. Ela pode impedir o retorno da imagem calculada depois que o contexto informa um erro. Não demonstra que o trabalho de compressão já realizado tenha sido desfeito. Os rascunhos do modelo omitiram essas diferenças e a segunda consulta. Propagar o erro aqui significa retornar o erro examinado; não há nova tentativa, tratador de exceções, ação compensatória ou garantia de execução bem-sucedida no método.

## O compressor concreto despacha depois da detecção

O método separado `Compressor.Compress` primeiro chama `imaging.DetectFormat(input)`. Seu caminho de erro diferente de nil retorna um resultado zero e esse erro antes do switch. O switch retorna diretamente de um auxiliar específico para cada um de oito formatos nomeados: JPEG, PNG, WebP, AVIF, HEIF, GIF, BMP e TIFF. O ramo HEIF também passa `detected.ContentType`; os demais ramos listados passam somente a entrada.

O ramo padrão do switch retorna um resultado zero com `imagecompression.ErrUnsupportedFormat`. Essas instruções mostram o despacho e o encaminhamento direto dos resultados dos auxiliares. Não estabelecem como cada codec valida dimensões, trata animação, altera metadados ou aloca memória, pois esses corpos de auxiliares estão ausentes do pacote. Detecção e codificação são responsabilidades diferentes na fonte; nenhuma equivale à política de contexto da aplicação.

## O que o capítulo corrigido estabelece

Os dois braços neurais usaram uma explicação genérica de compressão e omitiram os nomes de declaração exigidos pelo gravador. Acrescentar o método de despacho concreto não recuperou a ordem das verificações de contexto nem provou seu vínculo em execução. Esta correção preserva o resultado antecipado de entrada vazia, as duas consultas ao contexto, os caminhos de erro com resultado zero e o resultado final de sucesso; depois descreve o despacho concreto dentro de sua própria evidência. As saídas originais sem sucesso continuam como artefatos diagnósticos. Este é um candidato de documentação autoral, não um exemplo de treinamento aprovado, um rastreamento de execução da aplicação ou evidência de pesos alterados no modelo.
