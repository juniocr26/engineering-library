# Tarefas e iteração no Starlette: limites de chamada, retorno, yield e exceção

Correção experimental escrita pelo Codex e revisada contra a fonte, pendente de aprovação do proprietário. Revisão congelada do Starlette 271c277da0ff64e2048a4d46ecc812b9d61db5f6. Os baselines reais do agente local das ondas de contratos 2 e 3 estão preservados; nenhuma resposta completa foi aprovada. A correção combina explicitamente os dois arquivos na [evidência de fonte](../references/ref-c12c2a5ab43a824e7629.md). Nenhuma aplicação inspecionada foi executada.

## Argumentos preservados para a chamada

O construtor de `BackgroundTask` armazena o callable fornecido, a tupla de argumentos posicionais e o mapeamento de argumentos nomeados em campos separados. Também atribui a um campo o resultado de `is_async_callable(func)`. A implementação desse helper não está incluída nos dois arquivos selecionados; por isso, a correção não transforma seu nome em prova sobre a classificação de todo callable em execução. O construtor mostra o que é armazenado e qual expressão calcula a flag do ramo; não executa o callback armazenado.

O método assíncrono `__call__` testa `self.is_async`. No ramo verdadeiro, aguarda `self.func(*self.args, **self.kwargs)`. No outro ramo, aguarda `run_in_threadpool(self.func, *self.args, **self.kwargs)`. São dois caminhos escritos de chamada, sem comprovar que ambos executam ou que callbacks rodam concorrentemente. Não há return explícito nem tratador de exceção nesse método. A anotação e as entradas armazenadas, por si só, não estabelecem conclusão bem-sucedida ou tipo do resultado do callback.

## O helper retorna uma expressão aguardada

O corpo fornecido de `run_in_threadpool` primeiro reatribui seu parâmetro local func com `functools.partial(func, *args, **kwargs)`. Depois executa `return await anyio.to_thread.run_sync(func)`. Se essa expressão aguardada termina normalmente, este corpo retorna seu resultado. A resposta anterior do modelo local omitiu essa relação de retorno. O perfil determinístico de fatos da fonte a registra sem afirmar como partial ou run_sync implementa associação de argumentos, escalonamento, cancelamento ou transporte de exceções.

Os imports mostram de onde vêm os nomes escritos dos helpers. Não fornecem as implementações importadas. Em particular, o nome `run_in_threadpool` não basta para comprovar tamanho de pool, reutilização de threads, paralelismo ou desempenho. Nenhum callback do Starlette, operação AnyIO ou aplicação inspecionada foi executado nesta revisão. Fatos da fonte permanecem distintos de comportamento medido em execução.

## Uma coleção de tarefas aguarda seus elementos em ordem

`BackgroundTasks` inicializa `self.tasks` com `list(tasks)` quando o valor fornecido é verdadeiro e com uma lista vazia caso contrário. Seu método `add_task` constrói um `BackgroundTask` com o callable e os argumentos recebidos e acrescenta esse objeto. O código não invoca a nova tarefa dentro de `add_task`. O método de chamada percorre `self.tasks` e aguarda `task()` para cada elemento alcançado.

Esse laço aguarda a operação atual antes de avançar pelo laço escrito. Não contém criação de grupo de tarefas, operação de reunião nem try/except local. Uma exceção que escapa da tarefa aguardada não é capturada por esse corpo; portanto, a execução das iterações posteriores não é garantida. Isso não estabelece que trabalho independente do sistema para ou que a lista armazenada não possa mudar por outras referências. Uma descrição completa precisa separar construção da lista, acréscimo e invocação posterior.

## O esgotamento do iterador é traduzido e tratado com `break`

O arquivo define `_StopIteration` como subclasse de `Exception` com corpo `pass`. O helper `_next` tenta `return next(iterator)`. Seu tratador `except StopIteration` executa `raise _StopIteration`. Esse é o caminho mostrado de tradução; não há tratador para todo erro possível. A classe e o helper escritos permitem uma descrição mais precisa que inferir todo o comportamento pelo nome do wrapper de iteração, enquanto reatribuição real de nomes e comportamento de implementações importadas permanecem fora desta inspeção.

O gerador assíncrono `iterate_in_threadpool` atribui `iter(iterator)` a `as_iterator` antes de entrar em `while True`. Dentro do laço, tenta `yield await anyio.to_thread.run_sync(_next, as_iterator)`. Um resultado aguardado que conclui normalmente é emitido ao consumidor com yield; não é um valor final de return. Seu tratador `except _StopIteration` contém `break`. O baseline neural descreveu incorretamente esse tratador externo como relançamento da exceção. O helper lança o nome traduzido; o tratador externo escrito encerra seu laço. Essas operações pertencem a corpos diferentes.

O wrapper não contém else do laço, else do try ou finally e não demonstra limpeza de um iterador subjacente arbitrário. Outros erros não são capturados por esse tratador escrito específico, mas o resultado exato da correspondência de exceções em execução depende dos vínculos e da execução. Não há base na fonte para garantir lotes, novas tentativas ou pré-carregamento concorrente. O perfil derivado da fonte acrescentado na campanha anterior preserva inicializador, chamada emitida e `break` sem transformar helpers não resolvidos em fatos semânticos.

Este capítulo é um candidato corrigido de pesquisa, não uma melhoria dos pesos do modelo nem resposta aprovada para treinamento. A extensão determinística de iteração foi verificada nesta família real e em controles próprios; transferência independente para outro repositório real não foi estabelecida.

## FAQ de engenharia e evidência da classificação

<!-- reading-section: faq:await-expression-versus-return-value -->
### Aguardar BackgroundTask retorna o resultado do callback?

O método de tarefa selecionado aguarda uma expressão em cada ramo sem retorná-la. Se conclui normalmente, alcança o final e retorna `None`. O helper separado `run_in_threadpool` retorna seu resultado aguardado, mas o método de tarefa envolvente não encaminha esse valor. Isso decorre das [regras de retorno de funções Python](https://docs.python.org/3/tutorial/controlflow.html#defining-functions), não de uma execução do Starlette.

<!-- reading-section: faq:task-registration-versus-execution -->
### Adicionar uma tarefa a executa imediatamente ou cria trabalho paralelo?

O método mostrado constrói um objeto de tarefa e o acrescenta à lista. A chamada posterior da coleção aguarda cada tarefa alcançada em sequência. Esses métodos selecionados não estabelecem uma política de agendamento de resposta, outro processo ou fila distribuída.

<!-- reading-section: faq:async-callable-classifier-limit -->
### Todo callable que retorna um awaitable é classificado como assíncrono?

A fonte adicional do helper desembrulha objetos `functools.partial` e verifica o predicado de função coroutine no objeto ou em seu `__call__` callable. O vínculo desse predicado é importado por uma condição de versão do Python. Isso é mais restrito que examinar universalmente futuros valores retornados; implementações importadas dos predicados e escalonamento real continuam sem verificação.

O wrapper de iteração captura sua classe traduzida de esgotamento para encerrar o laço. Não fornece um finally que feche todo iterador subjacente possível. Falha do callback, esgotamento do iterador e limpeza pelo consumidor continuam contratos distintos.
