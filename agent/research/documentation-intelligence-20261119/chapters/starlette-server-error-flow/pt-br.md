# Middleware de erro de servidor: delegação de protocolo, estado da resposta e propagação

Correção escrita pelo Codex e revisada contra a fonte; pendente de aprovação do proprietário.

Starlette revision 271c277da0ff64e2048a4d46ecc812b9d61db5f6; actual preserved baseline: starlette-server-error-contract. [Exact source excerpts](source-excerpts.json).

## O ramo não HTTP ainda chama a aplicação

O baseline real do agente local afirmou que esse middleware só é chamado para HTTP. O método selecionado mostra outra fronteira: quando `scope["type"] != "http"`, aguarda `self.app(scope, receive, send)` e retorna. Portanto, o middleware pode ser invocado para outro tipo de escopo e delegá-lo. Essa chamada à aplicação fica fora do bloco try HTTP posterior e usa o callable send original.

Para HTTP, o método cria uma flag local `response_started`, inicialmente falsa, e define um emissor envolvente. Então aguarda `self.app(scope, receive, _send)` dentro do try. Esses são caminhos distintos, em vez de uma chamada universal usando o wrapper. Se a aplicação HTTP conclui normalmente, o método não tem retorno escrito de objeto de resposta; seu resultado declarado é None. Uma guarda de protocolo não deve ser confundida com a afirmação de que o objeto nunca pode receber um escopo não HTTP.

## A flag de início registra um caminho de mensagem, não entrega na rede

O wrapper verifica `message["type"] == "http.response.start"`. Quando essa comparação tem sucesso, define `response_started` como verdadeira antes de aguardar o `send(message)` original. A flag é capturada com nonlocal para essa invocação. Não é uma contagem de bytes entregues, uma confirmação de cliente ou um status de resposta de rede verificado.

Essa ordem importa quando o próprio emissor original falha: o marcador local já foi definido antes de essa chamada aguardada concluir. O corpo selecionado não valida toda sequência de mensagens ASGI nem estabelece que uma mensagem de início chegou à rede. Usa esse marcador local depois para decidir se invoca a resposta de erro gerada. O baseline percebeu uma flag de início em alto nível, mas seu texto em português alterou o identificador da fonte. Esta correção mantém `response_started` inalterado nos dois idiomas.

## Debug, tratamento padrão e customizado têm uma ordem

O ramo de erro HTTP é `except Exception as exc`. Ele constrói `Request(scope)` e então seleciona uma resposta. Um `self.debug` verdadeiro no teste de truthiness tem precedência e aguarda `run_in_threadpool(self.debug_response, request, exc)`. Caso contrário, `self.handler is None` seleciona a chamada síncrona padrão a `error_response`. Um handler customizado configurado alcança o predicado separado `is_async_callable`.

Quando esse predicado tem sucesso, o handler customizado é aguardado diretamente com request e exc. Caso contrário, é passado a `run_in_threadpool` com esses argumentos. Isso não significa que o método invoque as duas formas ou sempre invoque um handler customizado configurado no modo debug. O trecho do construtor armazena app, handler e debug, com handler tendo None como padrão e debug falso; essas anotações e atribuições não são validação em execução de todo objeto configurado possível.

## Os helpers fornecidos explicam a delegação sem provar escalonamento em execução

O corpo de `run_in_threadpool` expandido manualmente associa o callable e os argumentos com `functools.partial` e então retorna o resultado aguardado de `anyio.to_thread.run_sync(func)`. A fonte mostra propagação do resultado através desse helper. Não fornece observação em execução de uma thread de trabalho específica, política de cancelamento ou conclusão da aplicação.

A implementação fornecida de `is_async_callable` desembrulha repetidamente objetos `functools.partial`. Então testa `iscoroutinefunction` no objeto ou, se ele é callable, em seu membro `__call__`. Esse é o predicado escrito, não um classificador universal de todo objeto que possa retornar um awaitable. Os trechos dos construtores de resposta também são concretos: `error_response` constrói `PlainTextResponse` com o literal `Internal Server Error` e status 500; `debug_response` escolhe HTML quando o cabeçalho accept contém `text/html`, caso contrário texto simples, com status 500 nos dois ramos escritos. Seus helpers de formatação não foram expandidos para uma promessa sobre escaping ou conteúdo de traceback.

## Construir uma resposta e enviá-la são decisões diferentes

O bloco de seleção de resposta executa antes da verificação de `response_started`. Assim, mesmo quando uma resposta já começou segundo o marcador local, este corpo ainda seleciona e constrói sua resposta de erro, condicionado à conclusão normal dos helpers. Apenas o ramo posterior `if not response_started` aguarda `response(scope, receive, send)`, usando o emissor original. Dizer que o handler nunca é chamado após um evento de início exageraria essa guarda.

Depois que essas operações concluem, o `raise exc` explícito propaga a exceção capturada. O erro não é silenciado apenas porque uma resposta foi enviada. Se um handler ou a invocação da resposta lança erro antes, a instrução final pode não ser alcançada; o corpo não possui finally que force aquele raise original após toda falha possível de helper. Esta correção preserva a distinção entre trabalho de resposta de erro, envio e propagação. Reutiliza o baseline original concluído sem outro pedido ao modelo e continua pendente de revisão do proprietário, com fonte e avisos exatos retidos, sem publicação ou aprovação para treinamento.

## FAQ de engenharia

<!-- reading-section: faq:debug-handler-precedence -->
### O modo debug também invoca o handler de erro configurado?

O ramo de debug precede a seleção do handler customizado. Quando debug é verdadeiro no teste de truthiness e seu helper conclui normalmente, essa fonte seleciona a resposta de debug. Um handler customizado configurado não é chamado por esse caminho de seleção.

<!-- reading-section: faq:response-start-not-delivery-proof -->
### Uma mensagem de início de resposta prova que o cliente recebeu os cabeçalhos?

A flag local é definida antes de aguardar o emissor original. Uma falha do emissor pode, portanto, ocorrer depois que a flag muda. A flag controla a invocação posterior da resposta de erro; não é uma confirmação de entrega.

<!-- reading-section: faq:original-exception-rethrow -->
### A exceção original é silenciada depois de uma resposta gerada?

A operação final escrita lança a exceção capturada depois que as operações selecionadas anteriores concluem. Uma falha do handler ou da resposta pode impedir chegar a essa linha, pois não há finally que a force. A delegação separada não HTTP fica fora desse bloco de captura HTTP.

O construtor selecionado recebe aplicação, handler opcional e flag de debug. Este capítulo não verificou configuração de servidor, persistência, retry, autenticação ou uma implantação ASGI real; essas responsabilidades exigem sua própria fonte e evidência de execução.
