# Evidence record: chapters / starlette-task-and-iteration.json

This is a dated raw research artifact. Findings and rejected model outputs retain their recorded status. Reading the record does not approve publication or training.

SHA-256: `f3e42f2088fa6fdb4bc447cc4fc43a1ac03a6f11f46004a0bb20f5ccb0428228`. Original bytes: `42524`.

Original path: `agent/research/documentation-intelligence-20261119/body-claim-bundles-v1/chapters/starlette-task-and-iteration.json`.

<!-- reading-section:reference:f3e42f2088fa6fdb4bc4:consumers -->
## Referenced by

- [Per-chapter evidence review](../reviews/body-claims.md)

<!-- reading-section:reference:f3e42f2088fa6fdb4bc4:artifact -->
## Original artifact

The fenced contents reproduce the exact UTF-8 artifact; a display-only terminal newline is added if the original lacks one.

<!-- artifact-body:f3e42f2088fa6fdb4bc447cc4fc43a1ac03a6f11f46004a0bb20f5ccb0428228:start -->
````json
{
  "chapter": "starlette-task-and-iteration",
  "derived_review_artifact_not_new_chapter_or_training_example": true,
  "document_language_spans": 22,
  "owner_approved": false,
  "prose_groups": 11,
  "records": [
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 3,
          "last_line": 3,
          "quote": "Codex-authored source-reviewed experimental correction, pending owner approval. Frozen Starlette revision 271c277da0ff64e2048a4d46ecc812b9d61db5f6. Actual local-agent baselines from contract waves 2 and 3 are preserved; no whole baseline response was approved. The correction explicitly combines the two files in [source evidence](source-excerpts.json). No inspected application was executed.\n",
          "quote_sha256": "80768067d3a67ae8df1fafacb901b7f00812ccb575fc1a50e530171dace766a0"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 3,
          "last_line": 3,
          "quote": "Correção experimental escrita pelo Codex e revisada contra a fonte, pendente de aprovação do proprietário. Revisão congelada do Starlette 271c277da0ff64e2048a4d46ecc812b9d61db5f6. Os baselines reais do agente local das ondas de contratos 2 e 3 estão preservados; nenhuma resposta completa foi aprovada. A correção combina explicitamente os dois arquivos na [evidência de fonte](source-excerpts.json). Nenhuma aplicação inspecionada foi executada.\n",
          "quote_sha256": "7d91750a8025e193bfdf54dc8a721ac3931bd4a4eb12ef086a4648ef4673db89"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "cc50007a257993d37dd51281a202f3de9839bd7a84a8ae623065703c7b1e18bc"
        }
      ],
      "id": "starlette-task-and-iteration:body-paragraph:01",
      "manual_review_finding": "Pinnedtwooriginalfiles and retainedneuralbaselines; no inspectedapp execution or completebaselineapproval.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-210",
        "source-span-211"
      ],
      "status": "PROVENANCE",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 7,
          "last_line": 7,
          "quote": "The constructor of `BackgroundTask` stores the supplied callable, positional argument tuple and keyword mapping on separate fields. It also assigns the result of `is_async_callable(func)` to a field. The helper's implementation is not included in these two selected files, so the correction does not turn that name into a proof about every callable's runtime classification. The constructor shows what is stored and what expression computes the branch flag; it does not execute the stored callback.\n",
          "quote_sha256": "12d890e2f2da6ddd43ad923d4e12a27bf86ae7899a6a43f0bb968cd993c6d12e"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 7,
          "last_line": 7,
          "quote": "O construtor de `BackgroundTask` armazena o callable fornecido, a tupla de argumentos posicionais e o mapeamento de argumentos nomeados em campos separados. Também atribui a um campo o resultado de `is_async_callable(func)`. A implementação desse helper não está incluída nos dois arquivos selecionados; por isso, a correção não transforma seu nome em prova sobre a classificação de todo callable em execução. O construtor mostra o que é armazenado e qual expressão calcula a flag do ramo; não executa o callback armazenado.\n",
          "quote_sha256": "cc85cc25bd122c0e51aca968632ad4271a977d2a572358dd4c1fbe058a58a9f1"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:02",
      "manual_review_finding": "Constructor storesfunc/args/kwargs andclassificationexpression without invokingcallback; originaltwofiles excludeclassificationhelperbody.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-212"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 9,
          "last_line": 9,
          "quote": "The async `__call__` method tests `self.is_async`. On the truthy branch it awaits `self.func(*self.args, **self.kwargs)`. On the other branch it awaits `run_in_threadpool(self.func, *self.args, **self.kwargs)`. These are two written call paths, not evidence that both run or that callbacks run concurrently. There is no explicit return or exception handler in this method. Its annotation and stored inputs do not by themselves establish successful completion or the callback's result type.\n",
          "quote_sha256": "9d76261c030e2bcde4dbc1d660af1f4699e377ff6e6d41bd5c51a30298b7d5af"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 9,
          "last_line": 9,
          "quote": "O método assíncrono `__call__` testa `self.is_async`. No ramo verdadeiro, aguarda `self.func(*self.args, **self.kwargs)`. No outro ramo, aguarda `run_in_threadpool(self.func, *self.args, **self.kwargs)`. São dois caminhos escritos de chamada, sem comprovar que ambos executam ou que callbacks rodam concorrentemente. Não há return explícito nem tratador de exceção nesse método. A anotação e as entradas armazenadas, por si só, não estabelecem conclusão bem-sucedida ou tipo do resultado do callback.\n",
          "quote_sha256": "4a9c7a8621575b2783e10de3c62e55fe03ef7c4307260d3c19620dbbb269abb3"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:03",
      "manual_review_finding": "Twoexclusiveawaitpaths selectedbyis_async, no explicitreturn/catch or both/concurrent callbackexecutionproof.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-213"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 13,
          "last_line": 13,
          "quote": "The supplied `run_in_threadpool` body first reassigns its local func parameter with `functools.partial(func, *args, **kwargs)`. It then executes `return await anyio.to_thread.run_sync(func)`. If that awaited expression completes normally, this body returns its result. The earlier local-model answer omitted that return relationship. The deterministic source-fact profile records it without asserting how partial or run_sync implements argument binding, scheduling, cancellation or exception transport.\n",
          "quote_sha256": "f51b740a132ecec6b899ede2fff39523ae88e9b74a46f7d6e65accac34649db7"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 13,
          "last_line": 13,
          "quote": "O corpo fornecido de `run_in_threadpool` primeiro reatribui seu parâmetro local func com `functools.partial(func, *args, **kwargs)`. Depois executa `return await anyio.to_thread.run_sync(func)`. Se essa expressão aguardada termina normalmente, este corpo retorna seu resultado. A resposta anterior do modelo local omitiu essa relação de retorno. O perfil determinístico de fatos da fonte a registra sem afirmar como partial ou run_sync implementa associação de argumentos, escalonamento, cancelamento ou transporte de exceções.\n",
          "quote_sha256": "fc00ac47ec8693f3680aa5b31e8719c63eb8d87a083edf0efd6261ab8644f032"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:04",
      "manual_review_finding": "Partialrebind thenreturn-awaitedrun_sync result onnormalcompletion; not importedbinding/scheduling/cancellation guarantee.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-009"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 15,
          "last_line": 15,
          "quote": "The imports show where the written helper names come from. They do not supply the imported implementations. In particular, the name `run_in_threadpool` is insufficient evidence for pool size, thread reuse, parallelism or performance. No Starlette callback, AnyIO operation or inspected application was executed during this review. Source facts remain different from measured runtime behavior.\n",
          "quote_sha256": "03705e944a0e3eee884dc03a56af27214e3804566a07a5eb91ba2534ec79cab9"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 15,
          "last_line": 15,
          "quote": "Os imports mostram de onde vêm os nomes escritos dos helpers. Não fornecem as implementações importadas. Em particular, o nome `run_in_threadpool` não basta para comprovar tamanho de pool, reutilização de threads, paralelismo ou desempenho. Nenhum callback do Starlette, operação AnyIO ou aplicação inspecionada foi executado nesta revisão. Fatos da fonte permanecem distintos de comportamento medido em execução.\n",
          "quote_sha256": "6932dfec8551e1abf3d43dbcbfeaba166fa4000f1e162058b532216f52cd8805"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:05",
      "manual_review_finding": "Importnames do notestablishpoolsize/reuse/parallelism/performance or actualAnyIO execution.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-214",
        "source-span-215",
        "source-span-009"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 19,
          "last_line": 19,
          "quote": "`BackgroundTasks` initializes `self.tasks` with `list(tasks)` when the supplied value is truthy and with an empty list otherwise. Its `add_task` method constructs a `BackgroundTask` from the given callable and arguments, then appends that object. The code does not invoke the new task inside `add_task`. The call method iterates `self.tasks` and awaits `task()` for each element reached.\n",
          "quote_sha256": "d5fcacccb8d1929e76fe4209cca92bd169f216854c199e6f2fca538ce7121742"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 19,
          "last_line": 19,
          "quote": "`BackgroundTasks` inicializa `self.tasks` com `list(tasks)` quando o valor fornecido é verdadeiro e com uma lista vazia caso contrário. Seu método `add_task` constrói um `BackgroundTask` com o callable e os argumentos recebidos e acrescenta esse objeto. O código não invoca a nova tarefa dentro de `add_task`. O método de chamada percorre `self.tasks` e aguarda `task()` para cada elemento alcançado.\n",
          "quote_sha256": "c3b36ef4a87ada84d66bd9b5826ab27bb8ec35c93764e9d6364bbb93da50e867"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:06",
      "manual_review_finding": "Truthiness-basedlistinit, add_task constructs/appends withoutinvoking, laterloopawaitsreachedelements.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-216"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 21,
          "last_line": 21,
          "quote": "That loop awaits the current operation before advancing through the written loop. It contains no task-group creation, gathering operation or local try/except. An exception escaping an awaited task is not caught by this body, so later iterations are not guaranteed to execute. This does not establish that unrelated system work stops, or that the stored list cannot change through other references. A complete account must keep list construction, appending and eventual invocation separate.\n",
          "quote_sha256": "0c4cb28d8eb1a4842418f92831840fdb645cf44152003eb78e297150b05f6c15"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 21,
          "last_line": 21,
          "quote": "Esse laço aguarda a operação atual antes de avançar pelo laço escrito. Não contém criação de grupo de tarefas, operação de reunião nem try/except local. Uma exceção que escapa da tarefa aguardada não é capturada por esse corpo; portanto, a execução das iterações posteriores não é garantida. Isso não estabelece que trabalho independente do sistema para ou que a lista armazenada não possa mudar por outras referências. Uma descrição completa precisa separar construção da lista, acréscimo e invocação posterior.\n",
          "quote_sha256": "66c6aa59007dd0aeae6f352d5d86eae1f3aa3d0bfdac240ac6d577504c0da38e"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:07",
      "manual_review_finding": "Sequentialwrittenawaitloop hasnogather/taskgroup/localcatch; lateriterations notguaranteed afterexception, unrelatedsystemwork/listmutation separate.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-217"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 25,
          "last_line": 25,
          "quote": "The file defines `_StopIteration` as a subclass of `Exception` with a `pass` body. The helper `_next` attempts `return next(iterator)`. Its `except StopIteration` handler executes `raise _StopIteration`. This is the shown translation path; there is no handler for every possible error. The written class and helper support a more precise account than inferring all behavior from the iterator wrapper's name, while actual name rebinding and imported implementation behavior remain outside this inspection.\n",
          "quote_sha256": "115a4720f5cc5f13521fae4de11a72c041f729582c18470b1b6cd84a5c8eb6c9"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 25,
          "last_line": 25,
          "quote": "O arquivo define `_StopIteration` como subclasse de `Exception` com corpo `pass`. O helper `_next` tenta `return next(iterator)`. Seu tratador `except StopIteration` executa `raise _StopIteration`. Esse é o caminho mostrado de tradução; não há tratador para todo erro possível. A classe e o helper escritos permitem uma descrição mais precisa que inferir todo o comportamento pelo nome do wrapper de iteração, enquanto reatribuição real de nomes e comportamento de implementações importadas permanecem fora desta inspeção.\n",
          "quote_sha256": "dbea02feed9812e0022e286901ca1a211d41bcfa727a7f90c9d461831376ce34"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:08",
      "manual_review_finding": "_StopIterationclass andnext-return helpertranslateonlyStopIteration into newname; no catchall orruntimebinding guarantee.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-218"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 27,
          "last_line": 27,
          "quote": "The async generator `iterate_in_threadpool` assigns `iter(iterator)` to `as_iterator` before entering `while True`. Within the loop it tries `yield await anyio.to_thread.run_sync(_next, as_iterator)`. A normally completed awaited result is yielded to the consumer; it is not a final return value. Its `except _StopIteration` handler contains `break`. The neural baseline incorrectly described this outer handler as reraising the exception. The helper raises the translated name; the outer written handler terminates its loop. Those operations belong to different bodies.\n",
          "quote_sha256": "742f5f56c337c37c0f88e6e7a33d8c3a38bc14806961b1de97437ca36718e578"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 27,
          "last_line": 27,
          "quote": "O gerador assíncrono `iterate_in_threadpool` atribui `iter(iterator)` a `as_iterator` antes de entrar em `while True`. Dentro do laço, tenta `yield await anyio.to_thread.run_sync(_next, as_iterator)`. Um resultado aguardado que conclui normalmente é emitido ao consumidor com yield; não é um valor final de return. Seu tratador `except _StopIteration` contém `break`. O baseline neural descreveu incorretamente esse tratador externo como relançamento da exceção. O helper lança o nome traduzido; o tratador externo escrito encerra seu laço. Essas operações pertencem a corpos diferentes.\n",
          "quote_sha256": "89c5304b68f3947ee832aedc5099c6c8057987b94b5e7bb7b7fc35fdaed44e82"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:09",
      "manual_review_finding": "Iterinitializationbeforeloop, awaitedresultyield notreturn, translated-exceptionhandlerbreaks notreraises.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-219"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 29,
          "last_line": 29,
          "quote": "The wrapper contains no loop else, try else or finally and does not demonstrate cleanup of an arbitrary underlying iterator. Other errors are not caught by this specific written handler, but the exact runtime exception-matching outcome depends on bindings and execution. There is no source basis for a batching, retry or concurrent-prefetch guarantee. The source-derived profile added in the previous campaign preserves the initializer, yielded call and `break` without converting unresolved helpers into semantic facts.\n",
          "quote_sha256": "17b221b046f039adb57cf949fb2b2ab2bbdf432794b3250832a9831f19d5b843"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 29,
          "last_line": 29,
          "quote": "O wrapper não contém else do laço, else do try ou finally e não demonstra limpeza de um iterador subjacente arbitrário. Outros erros não são capturados por esse tratador escrito específico, mas o resultado exato da correspondência de exceções em execução depende dos vínculos e da execução. Não há base na fonte para garantir lotes, novas tentativas ou pré-carregamento concorrente. O perfil derivado da fonte acrescentado na campanha anterior preserva inicializador, chamada emitida e `break` sem transformar helpers não resolvidos em fatos semânticos.\n",
          "quote_sha256": "0e5e60b6a40e06bd988ee9adab4796501bf861a57b0251ddfb20df753bf96e1b"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [],
      "id": "starlette-task-and-iteration:body-paragraph:10",
      "manual_review_finding": "No loop/tryelse orfinally cleanup, batching/retry/prefetch guarantee; exactruntimeexceptionmatching conditional onbindings.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-219"
      ],
      "status": "SOURCE_SUPPORTED_WITH_LIMITS",
      "training_gold": false
    },
    {
      "bilingual_document_spans": {
        "en": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/en.md",
          "document_sha256": "7499809154d35681c525d7d69fc6c490ea43485f00433335c1152cb08fc10269",
          "first_line": 31,
          "last_line": 31,
          "quote": "This chapter is a corrected research candidate, not a model-weight improvement or approved training answer. The deterministic iteration extension was verified on this actual family and owned controls; independent real-repository transfer is not established.\n",
          "quote_sha256": "2c6603f4bfeb7326a673ccab1e0b7a0fb7c665139ecd0b1c9f28fa7b437849c2"
        },
        "pt-br": {
          "document": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/pt-br.md",
          "document_sha256": "eea252b07c7eaf0b22251ac03ffbff086931217f83501b8378154a6c98d49f3c",
          "first_line": 31,
          "last_line": 31,
          "quote": "Este capítulo é um candidato corrigido de pesquisa, não uma melhoria dos pesos do modelo nem resposta aprovada para treinamento. A extensão determinística de iteração foi verificada nesta família real e em controles próprios; transferência independente para outro repositório real não foi estabelecida.\n",
          "quote_sha256": "d42e8cb03f8ce7d392f00c5f003ba17d84e47c4f557877eb61c879773524dae9"
        }
      },
      "bilingual_review": "Readpairedprose andactualsources; checked getterownership/truthiness, bare-superwording, inputnamevslookupsymbol, mappresence/prefix, await/yield/break and runtime caveats. Inlineidentifiers match.",
      "chapter": "starlette-task-and-iteration",
      "execution_or_inspection_receipts": [
        {
          "path": "agent/research/documentation-intelligence-20261119/chapters/starlette-task-and-iteration/review.json",
          "role": "Dated review/inspection or historical owned language-probe result, not a new external application execution.",
          "sha256": "cc50007a257993d37dd51281a202f3de9839bd7a84a8ae623065703c7b1e18bc"
        }
      ],
      "id": "starlette-task-and-iteration:body-paragraph:11",
      "manual_review_finding": "Deterministiciterationprofile checked onthisfamily/ownedcontrols only; not neuraltraining or independentrealrepotransfer.",
      "owner_approved": false,
      "scope": "PreFAQproseonly; headings/tables/fences/FAQ excluded.",
      "source_span_ids": [
        "source-span-219"
      ],
      "status": "REVIEW_PROCESS_AND_SOURCE",
      "training_gold": false
    }
  ],
  "schema": "chapter-specific-body-claim-review-v1",
  "scope": "Proseparagraphs beforefirstFAQheading only; titles,tables,fences,FAQ/trailingcontext andgenericatomicentailment are separate.",
  "source_spans": [
    {
      "first_line": 32,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/concurrency.py",
      "full_file_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "id": "source-span-009",
      "last_line": 34,
      "quote": "async def run_in_threadpool(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:\n    func = functools.partial(func, *args, **kwargs)\n    return await anyio.to_thread.run_sync(func)\n",
      "quote_sha256": "d6ae32f8faf0bafe2369d4009f7e3726f921da3364396d74dd868a28216a66cc",
      "repository": "starlette",
      "revision": "271c277da0ff64e2048a4d46ecc812b9d61db5f6",
      "source_path": "starlette/concurrency.py"
    },
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-210",
      "last_line": 36,
      "quote": "from __future__ import annotations\n\nfrom collections.abc import Callable, Sequence\nfrom typing import Any, ParamSpec\n\nfrom starlette._utils import is_async_callable\nfrom starlette.concurrency import run_in_threadpool\n\nP = ParamSpec(\"P\")\n\n\nclass BackgroundTask:\n    def __init__(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:\n        self.func = func\n        self.args = args\n        self.kwargs = kwargs\n        self.is_async = is_async_callable(func)\n\n    async def __call__(self) -> None:\n        if self.is_async:\n            await self.func(*self.args, **self.kwargs)\n        else:\n            await run_in_threadpool(self.func, *self.args, **self.kwargs)\n\n\nclass BackgroundTasks(BackgroundTask):\n    def __init__(self, tasks: Sequence[BackgroundTask] | None = None):\n        self.tasks = list(tasks) if tasks else []\n\n    def add_task(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:\n        task = BackgroundTask(func, *args, **kwargs)\n        self.tasks.append(task)\n\n    async def __call__(self) -> None:\n        for task in self.tasks:\n            await task()\n",
      "quote_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/concurrency.py",
      "full_file_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "id": "source-span-211",
      "last_line": 59,
      "quote": "from __future__ import annotations\n\nimport functools\nimport warnings\nfrom collections.abc import AsyncIterator, Callable, Coroutine, Iterable, Iterator\nfrom typing import ParamSpec, TypeVar\n\nimport anyio.to_thread\n\nfrom starlette.exceptions import StarletteDeprecationWarning\n\nP = ParamSpec(\"P\")\nT = TypeVar(\"T\")\n\n\nasync def run_until_first_complete(*args: tuple[Callable, dict]) -> None:  # type: ignore[type-arg]\n    warnings.warn(\n        \"run_until_first_complete is deprecated and will be removed in a future version.\",\n        StarletteDeprecationWarning,\n    )\n\n    async with anyio.create_task_group() as task_group:\n\n        async def run(func: Callable[[], Coroutine]) -> None:  # type: ignore[type-arg]\n            await func()\n            task_group.cancel_scope.cancel()\n\n        for func, kwargs in args:\n            task_group.start_soon(run, functools.partial(func, **kwargs))\n\n\nasync def run_in_threadpool(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:\n    func = functools.partial(func, *args, **kwargs)\n    return await anyio.to_thread.run_sync(func)\n\n\nclass _StopIteration(Exception):\n    pass\n\n\ndef _next(iterator: Iterator[T]) -> T:\n    # We can't raise `StopIteration` from within the threadpool iterator\n    # and catch it outside that context, so we coerce them into a different\n    # exception type.\n    try:\n        return next(iterator)\n    except StopIteration:\n        raise _StopIteration\n\n\nasync def iterate_in_threadpool(\n    iterator: Iterable[T],\n) -> AsyncIterator[T]:\n    as_iterator = iter(iterator)\n    while True:\n        try:\n            yield await anyio.to_thread.run_sync(_next, as_iterator)\n        except _StopIteration:\n            break\n",
      "quote_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/concurrency.py"
    },
    {
      "first_line": 12,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-212",
      "last_line": 17,
      "quote": "class BackgroundTask:\n    def __init__(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:\n        self.func = func\n        self.args = args\n        self.kwargs = kwargs\n        self.is_async = is_async_callable(func)\n",
      "quote_sha256": "3fdffb48a53b6fd837bcdaf3b3b0726cfc9139f95be5bd502931f09523d4ce5c",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 19,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-213",
      "last_line": 23,
      "quote": "    async def __call__(self) -> None:\n        if self.is_async:\n            await self.func(*self.args, **self.kwargs)\n        else:\n            await run_in_threadpool(self.func, *self.args, **self.kwargs)\n",
      "quote_sha256": "eefe65980ba39eb785d74ca27e9e00c77dd2837593c79c04f6fea61eecfcc7e1",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-214",
      "last_line": 7,
      "quote": "from __future__ import annotations\n\nfrom collections.abc import Callable, Sequence\nfrom typing import Any, ParamSpec\n\nfrom starlette._utils import is_async_callable\nfrom starlette.concurrency import run_in_threadpool\n",
      "quote_sha256": "b942643f193ae2068d9fe0f72c376ea6d7a16ab90e81b6035571348a0fa2116c",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 1,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/concurrency.py",
      "full_file_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "id": "source-span-215",
      "last_line": 10,
      "quote": "from __future__ import annotations\n\nimport functools\nimport warnings\nfrom collections.abc import AsyncIterator, Callable, Coroutine, Iterable, Iterator\nfrom typing import ParamSpec, TypeVar\n\nimport anyio.to_thread\n\nfrom starlette.exceptions import StarletteDeprecationWarning\n",
      "quote_sha256": "1a5ad10ad8666b828592ff36a5e804488bf744c769c5a8764f3532603af8bd9e",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/concurrency.py"
    },
    {
      "first_line": 26,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-216",
      "last_line": 36,
      "quote": "class BackgroundTasks(BackgroundTask):\n    def __init__(self, tasks: Sequence[BackgroundTask] | None = None):\n        self.tasks = list(tasks) if tasks else []\n\n    def add_task(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:\n        task = BackgroundTask(func, *args, **kwargs)\n        self.tasks.append(task)\n\n    async def __call__(self) -> None:\n        for task in self.tasks:\n            await task()\n",
      "quote_sha256": "cd7d651496cfbd3f1dbea207665de909dde18376a75ff179f0a1d1359ea57840",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 34,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/background.py",
      "full_file_sha256": "0fe5e952915181406765e035b4783330e82e6dee8809564594e03830bd2ad53f",
      "id": "source-span-217",
      "last_line": 36,
      "quote": "    async def __call__(self) -> None:\n        for task in self.tasks:\n            await task()\n",
      "quote_sha256": "75a811addcf750022c485fe20c6de056fa0db72aa85ee90d88c443e2b5da3115",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/background.py"
    },
    {
      "first_line": 37,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/concurrency.py",
      "full_file_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "id": "source-span-218",
      "last_line": 48,
      "quote": "class _StopIteration(Exception):\n    pass\n\n\ndef _next(iterator: Iterator[T]) -> T:\n    # We can't raise `StopIteration` from within the threadpool iterator\n    # and catch it outside that context, so we coerce them into a different\n    # exception type.\n    try:\n        return next(iterator)\n    except StopIteration:\n        raise _StopIteration\n",
      "quote_sha256": "b7c323bf69c7008b810498d9aae1603534904bc2edf5c65b22e785286b3e5deb",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/concurrency.py"
    },
    {
      "first_line": 51,
      "frozen_source": ".local-backups/documentation-intelligence-20261119/chapter-source-verification-v1/sources/starlette/starlette/concurrency.py",
      "full_file_sha256": "3e9e245d060ef39716c58ed754db7995c62f8581d4aaec8b82e09e73b84a2a83",
      "id": "source-span-219",
      "last_line": 59,
      "quote": "async def iterate_in_threadpool(\n    iterator: Iterable[T],\n) -> AsyncIterator[T]:\n    as_iterator = iter(iterator)\n    while True:\n        try:\n            yield await anyio.to_thread.run_sync(_next, as_iterator)\n        except _StopIteration:\n            break\n",
      "quote_sha256": "bd2f57f863cd93964eedebc523ecca61494b9fe3a59592b8413baa2339357bda",
      "repository": "starlette",
      "revision": {
        "kind": "frozen-Git-commit",
        "value": "271c277da0ff64e2048a4d46ecc812b9d61db5f6"
      },
      "source_path": "starlette/concurrency.py"
    }
  ],
  "status": "CODEX_SOURCE_REVIEW_PENDING_OWNER",
  "training_gold": false
}
````
<!-- artifact-body:f3e42f2088fa6fdb4bc447cc4fc43a1ac03a6f11f46004a0bb20f5ccb0428228:end -->
