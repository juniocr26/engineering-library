# Dimensões de imagens estáticas: delegação, guardas e aritmética

Rascunho experimental escrito pelo Codex e revisado na fonte; a aprovação humana e a publicação estão pendentes. Fonte: go-image-optimizer na revisão `48476de6e4450294b7769ab7af90805100bb21b5`, `backend/internal/infrastructure/imaging/limits.go`. O baseline e o braço com auxiliar do agente local, `gio-dimensions-caller` e `gio-dimensions-helpers`, permanecem preservados. A aplicação não foi executada, e esta correção não representa treinamento neural.

## Dois parâmetros na fronteira do wrapper

A declaração `ValidateDimensions(cfg image.Config, maxPixels int) error` recebe um objeto de configuração e um orçamento de pixels. Ela não recebe parâmetros separados de largura e altura. O corpo chama `ValidateImageSize(cfg.Width, cfg.Height, maxPixels)` e retorna diretamente seu resultado. Largura e altura são extraídas dos campos da configuração no ponto de chamada; o orçamento é encaminhado como terceiro argumento. O wrapper não reconstrói uma configuração nem aloca uma imagem.

Essa distinção importa porque o baseline do modelo inventou quatro entradas: configuração, largura, altura e máximo de pixels. Também confundiu metadados do preparador opcional de fonte com o contrato da aplicação. Metadados do parser podem identificar uma declaração e sua citação; não se tornam outro parâmetro da aplicação nem estabelecem validação semântica. O trecho isolado do wrapper permite relatar a delegação e as expressões dos argumentos. O corpo do auxiliar é necessário para explicar os ramos de validação abaixo.

## Dimensões inválidas têm prioridade

O auxiliar `ValidateImageSize` recebe largura, altura e orçamento como inteiros. Sua primeira condição é `width <= 0 || height <= 0`. Qualquer dimensão não positiva leva imediatamente a `imageprocessing.ErrInvalidImage`. As duas dimensões precisam ser positivas para ultrapassar essa guarda. O operador lógico significa que uma dimensão inválida basta; exigir que ambas fossem inválidas mudaria o contrato.

Esse retorno antecipado também define a ordem da aritmética. O auxiliar não avalia a divisão posterior quando qualquer dimensão já falhou na primeira guarda. Em particular, a altura escrita como divisor é positiva no caminho que alcança a segunda condição. Essa é uma observação local sobre o fluxo de controle, não uma prova sobre identidades de erros importados ou sobre a correção de um decodificador. O auxiliar examina inteiros fornecidos pelo chamador; ele não analisa bytes de uma imagem codificada.

## A comparação com o orçamento é estrita

A segunda condição é `width > maxPixels/height`. Quando verdadeira, o auxiliar retorna `imageprocessing.ErrImageTooLarge`. Quando falsa, o resultado final é `nil`. A comparação é estrita: a igualdade com o quociente inteiro não segue esse ramo de erro. Descrever a condição como maior ou igual rejeitaria um limite adicional. O código expressa uma divisão em vez de multiplicar largura por altura; a explicação deve preservar a aritmética escrita, sem apresentar um produto não verificado como implementação.

O corpo não contém uma verificação separada de positividade do orçamento. Essa ausência não significa que todo valor de orçamento tenha sucesso; seu efeito decorre da divisão inteira e da comparação existentes. Com largura e altura positivas e orçamento zero, o quociente é zero e a comparação estrita reprova a validação. Este capítulo não transforma a função em uma especificação completa de política numérica nem infere restrições que outro chamador possa impor.

## Uma constante padrão não é um padrão automático do wrapper

O arquivo declara `DefaultMaxDecodedPixels` como `32_000_000`. Seu comentário motiva o limite com o crescimento da memória decodificada e um exemplo RGBA aproximado. O wrapper estático, porém, usa o orçamento fornecido pelo chamador. Não seleciona essa constante internamente. Outras funções no mesmo arquivo podem escolhê-la de forma explícita; compartilhar um arquivo não a torna valor implícito de parâmetro em toda chamada.

A resposta neural com auxiliar mencionou dimensões positivas, mas omitiu a divisão exata, os caminhos de erro distintos e o retorno nil normal. Também atribuiu comportamento do auxiliar à citação separada do chamador. Por isso, a evidência corrigida preserva as duas declarações e suas próprias localizações. Selecionar a fonte e conferir citações literais com sucesso não prova que a explicação preserve papéis de parâmetros, retornos antecipados ou operadores de limite. Este capítulo é um candidato revisado para aprovação humana posterior, sem alegações sobre execução real de decodificadores, consumo de memória ou comportamento de rede.

## FAQ de engenharia

<!-- reading-section: faq:wrapper-parameters -->
### O wrapper recebe largura e altura como parâmetros separados?

Ele recebe uma configuração e um orçamento de pixels. Extrai os campos de largura e altura ao chamar o helper. Metadados do parser e essas expressões de argumentos não acrescentam parâmetros à declaração do wrapper.

<!-- reading-section: faq:quotient-equality -->
### A igualdade com o quociente inteiro do orçamento é rejeitada?

A comparação escrita é estritamente maior que. Depois que dimensões positivas passam pela guarda anterior, igualdade com o quociente evita esse ramo de erro. Dimensões não positivas retornam seu próprio erro anterior antes da divisão.

<!-- reading-section: faq:explicit-budget-argument -->
### O wrapper estático usa automaticamente o padrão nomeado?

Ele encaminha sem alteração o orçamento do chamador. O padrão nomeado é uma declaração separada. O [validador de animação](../go-image-animation/pt-br.md) seleciona explicitamente esse padrão estático antes de sua verificação agregada distinta; essas escolhas não devem ser fundidas.

O orçamento trata de pixels, não bytes codificados ou limite exato de memória residente. Validade do decodificador, identidades dos erros importados e uso observado de memória permanecem fora desta revisão de fonte.
