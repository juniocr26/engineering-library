# FastAPI: do handler de rota às dependências e à resposta

Este capítulo de caminho selecionado descreve `fastapi/fastapi` em `05e6df7e906c3decba377c37548019973f40bf15`. Conecta a factory do handler de rota, a chamada de dependências de um handler HTTP normal, a inicialização do cache, os valores do endpoint e a serialização condicional. A evidência é código estático fixado, com licença MIT. Isso não é compreensão completa do projeto, uma requisição executada ou aprovação do proprietário.

## Factory e passagem para as dependências

`APIRoute.get_route_handler` começa com uma visão de rota de `self`. Lê `_effective_route_context_var`; quando o contexto não é `None` e seu `original_route is self`, usa esse contexto efetivo como visão de rota. Retorna `get_request_handler(...)`, passando `route.dependant`, `route.dependency_overrides_provider` e outras opções de rota. Portanto, o código não justifica simplificar todo argumento para uma propriedade do `self` original. Evidência: `fastapi/routing.py:1322–1347`.

`get_request_handler` retorna sua função assíncrona aninhada `app(request)`. Nessa função, a chamada selecionada de `solve_dependencies` passa a requisição, o dependant, o corpo já analisado, o provedor de overrides, o argumento de stack e o indicador de incorporação de campos do corpo. Não passa a keyword `dependency_cache` e não possui desempacotamento de keywords que pudesse fornecê-la. O módulo importa o solver diretamente de `fastapi.dependencies.utils`. Evidência: `fastapi/routing.py:406–438,528–535,821` e a declaração de importação fixada.

O tratamento anterior do corpo e as assertions de stack podem impedir que essa chamada seja alcançada. O capítulo descreve a passagem selecionada, não todas as condições para aceitar uma requisição HTTP real.

## Propriedade do cache: limite de uma invocação

O parâmetro keyword-only `dependency_cache` do solver tem padrão `None`. Seu ramo escrito `if dependency_cache is None` atribui um novo dicionário vazio a esse nome local. Assim, quando a chamada selecionada do handler alcança esse ramo usando o argumento padrão, a inicialização ocorre dentro dessa invocação do solver. Evidência: `fastapi/dependencies/utils.py:671–701`.

Dentro do laço de dependências, a chamada recursiva do solver passa `dependency_cache=dependency_cache`. O construtor retornado de `SolvedDependency` também recebe esse cache local. São passagens explícitas do mesmo nome local no fluxo escrito selecionado. Evidência: `fastapi/dependencies/utils.py:704–737,823–829`.

Isso não prova que uma requisição inteira tenha exatamente um cache, que todo chamador omita o parâmetro ou que valores de dependências sejam globalmente isolados ou seguros entre threads. Outros pontos de entrada e objetos de cache fornecidos pelo chamador estão fora deste contrato. A construção das chaves e a política de leitura/escrita do cache são assuntos separados. O solver também lê os dois objetos de stack de `request.scope` e contém assertions escritas de tipo; passar apenas o argumento legado de stack não estabelece a propriedade da limpeza ou um runtime com assertions habilitadas. Evidência: `fastapi/dependencies/utils.py:679–693`.

## Valores alcançam um caminho condicional do endpoint

A chamada selecionada de `run_endpoint_function` passa `values=solved_result.values`. Suas condições envolventes incluem o ramo verdadeiro de `not errors` e os ramos else de `is_sse_stream`, `is_json_stream` e da verificação de callable gerador. Os caminhos de streaming e geradores têm outro código; o capítulo não afirma que eles nunca invoquem endpoints. Evidência: `fastapi/routing.py:541,572,703,739,762–766`.

Em `run_endpoint_function`, o ramo de coroutine aguarda `dependant.call(**values)`. O outro ramo delega a `run_in_threadpool` com `_run_sync_endpoint`, o callable e `arguments=values`. Também há uma assertion escrita sobre o callable. Isso é estrutura do código, não evidência de que algum endpoint tenha efetivamente executado. Evidência: `fastapi/routing.py:372–385`.

## Serialização e limites de erro

Depois dessa chamada selecionada do endpoint, uma `Response` retornada é usada em seu próprio ramo. A chamada selecionada de `serialize_response` fica no ramo else de `isinstance(raw_response, Response)` e passa `response_content=raw_response`. Mantém as condições anteriores de ausência de erros e dos ramos sem stream/gerador. Portanto, nem todo retorno de endpoint necessariamente passa por essa chamada de serialização. Evidência: `fastapi/routing.py:762–796`.

O ramo posterior `if errors` constrói e lança `RequestValidationError`. Separadamente, `serialize_response` contém um ramo de erro de validação do campo que lança `ResponseValidationError`; sem um campo, seu ramo else chama `jsonable_encoder`. São limites distintos de erro de requisição e resposta escritos no código. Não prometem ausência de outras exceções. Evidência: `fastapi/routing.py:808–815,329–369`.

## Um fragmento com a forma da API

O fragmento próprio abaixo ilustra os nomes das keywords obrigatórias do solver sem fornecer um cache. Pressupõe que o vínculo do solver e os argumentos já foram fornecidos, incluindo um escopo de requisição preparado adequadamente. Não é um servidor independente nem uma recomendação para ignorar o middleware de roteamento.

```python
async def resolve_selected(request, dependant, stack, embed_body_fields):
    return await solve_dependencies(
        request=request,
        dependant=dependant,
        async_exit_stack=stack,
        embed_body_fields=embed_body_fields,
    )
```

A sintaxe Python e a forma das keywords obrigatórias selecionadas são verificadas. Importações, anotações, preparação da requisição, contratos de callbacks e sucesso em runtime não são testados. O handler efetivo também passa argumentos de corpo e overrides; os argumentos opcionais omitidos aqui usam os padrões declarados do solver.

## Testes e FAQ

O arquivo fixado `tests/test_dependency_cache.py:64–71` escreve `test_sub_counter`: redefine o contador, faz duas chamadas à rota de subcontador e verifica pares iguais de counter/subcounter de 1/1 e depois 2/2, com assertions de status. Isso é evidência escrita de um cenário pretendido de dependência repetida, não um resultado observado de aprovação ou prova de todo ramo do handler. `tests/test_dependency_yield_scope.py` também está preservado, mas sua mera presença não estabelece duração universal do cache. Nenhuma suíte de testes ou aplicação FastAPI foi executada nesta campanha. Os testes existentes da Engineering Library são uma população separada.

**Há um único cache comprovado para toda requisição?** Não. O limite verificado de inicialização é a invocação selecionada do solver que recebe seu padrão `None`, com passagem recursiva do cache local.

**A chamada selecionada do endpoint executa quando há erros do solver?** Não. Essa chamada está dentro do ramo `not errors`, com restrições adicionais de ramo. Exceções anteriores também podem interromper o caminho.

**Todo resultado bruto do endpoint é serializado aqui?** Não. A chamada selecionada de serialização está no ramo que não é `Response`, depois do caminho ordinário selecionado do endpoint.

**A factory sempre usa a visão de rota original?** Não. Sua condição escrita de contexto efetivo pode selecionar outra visão para os argumentos do handler. Isso não certifica todo chamador que define o contexto ou vínculo em runtime.

## Limites da verificação

Um observador de AST léxico registra chamadas e as condições if/laço que as envolvem. Consultas separadas obtêm novamente objetos públicos exatos do Git e verificam importações, argumentos, padrões, ramos selecionados e contagens conservadoras de vínculos. Essas consultas não estabelecem fluxo de controle completo, verdade de prosa arbitrária, comportamento de monkey-patching dinâmico ou integração completa. Formas incorretas de código sintético são controles de desenvolvimento, não projetos independentes de avaliação. Este capítulo isolado aguarda revisão concluída; publicação, integração ao catálogo ativo, aprovação do proprietário e gold de treinamento permanecem falsos.
