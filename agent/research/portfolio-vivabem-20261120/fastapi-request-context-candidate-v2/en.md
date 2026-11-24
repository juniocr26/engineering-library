# FastAPI: from a route handler to dependencies and a response

This selected-path chapter describes `fastapi/fastapi` at `05e6df7e906c3decba377c37548019973f40bf15`. It connects the route handler factory, a normal HTTP handler's dependency call, cache initialization, endpoint values and conditional serialization. Evidence is static, pinned MIT-licensed source. This is not complete project understanding, an executed request or owner approval.

## Factory and dependency handoff

`APIRoute.get_route_handler` begins with a route view of `self`. It reads `_effective_route_context_var`; when the context is not `None` and its `original_route is self`, it uses that effective context as the route view. It returns `get_request_handler(...)`, passing `route.dependant`, `route.dependency_overrides_provider` and other route options. Thus the source does not justify simplifying every argument to a property of the original `self`. Evidence: `fastapi/routing.py:1322–1347`.

`get_request_handler` returns its nested asynchronous `app(request)` function. In that function, the selected `solve_dependencies` call passes the request, dependant, parsed body, overrides provider, stack argument and body-embedding flag. It passes no `dependency_cache` keyword and has no keyword unpacking that could supply one. The module imports the solver directly from `fastapi.dependencies.utils`. Evidence: `fastapi/routing.py:406–438,528–535,821` and the frozen import declaration.

Earlier body handling and stack assertions can prevent this call from being reached. The chapter describes the selected handoff, not every condition for accepting a real HTTP request.

## Cache ownership: an invocation boundary

The solver's keyword-only `dependency_cache` parameter defaults to `None`. Its written `if dependency_cache is None` branch assigns a new empty dictionary to that local name. Therefore, when the selected handler call reaches this branch using the default argument, initialization occurs inside that solver invocation. Evidence: `fastapi/dependencies/utils.py:671–701`.

Inside the dependency loop, the recursive solver call passes `dependency_cache=dependency_cache`. The returned `SolvedDependency` constructor also receives that local cache. These are explicit handoffs of the same local name in the selected written flow. Evidence: `fastapi/dependencies/utils.py:704–737,823–829`.

This is not a proof that an entire request has exactly one cache, that every caller omits the parameter, or that dependency values are globally isolated or thread-safe. Other entry points and caller-supplied cache objects are outside this contract. Cache-key construction and read/write policy are separate topics. The solver also reads the two stack objects from `request.scope` and contains written type assertions; passing the legacy stack argument alone does not establish cleanup ownership or assertion-enabled runtime behavior. Evidence: `fastapi/dependencies/utils.py:679–693`.

## Values reach one conditional endpoint path

The selected `run_endpoint_function` call passes `values=solved_result.values`. Its enclosing conditions include the true branch of `not errors` and the else branches for `is_sse_stream`, `is_json_stream`, and the generator-callable check. Streaming and generator paths have other code; this chapter does not claim that they never invoke endpoints. Evidence: `fastapi/routing.py:541,572,703,739,762–766`.

Within `run_endpoint_function`, the coroutine branch awaits `dependant.call(**values)`. The other branch delegates to `run_in_threadpool` with `_run_sync_endpoint`, the callable and `arguments=values`. There is also a written assertion about the callable. This is source structure, not evidence that either endpoint actually ran. Evidence: `fastapi/routing.py:372–385`.

## Serialization and error boundaries

After that selected endpoint call, a returned `Response` is used by its own branch. The selected `serialize_response` call is in the else branch of `isinstance(raw_response, Response)` and passes `response_content=raw_response`. It retains the preceding non-error and non-stream/generator conditions. Consequently, not every endpoint return necessarily goes through that serialization call. Evidence: `fastapi/routing.py:762–796`.

The later `if errors` branch constructs and raises `RequestValidationError`. Separately, `serialize_response` contains a field-validation error branch that raises `ResponseValidationError`; without a field, its else branch calls `jsonable_encoder`. These are distinct written request/response error boundaries. They do not promise the absence of other exceptions. Evidence: `fastapi/routing.py:808–815,329–369`.

## A source-shaped API fragment

The following owned fragment illustrates the required solver keyword names without supplying a cache. It assumes the solver binding and arguments are already supplied, including an appropriately prepared request scope. It is not a standalone server or a recommendation to bypass routing middleware.

```python
async def resolve_selected(request, dependant, stack, embed_body_fields):
    return await solve_dependencies(
        request=request,
        dependant=dependant,
        async_exit_stack=stack,
        embed_body_fields=embed_body_fields,
    )
```

Python syntax and the selected required keyword shape are checked. Imports, annotations, request preparation, callback contracts and runtime success are not tested. The actual handler additionally passes body and overrides arguments; omitted optional arguments here use the declared solver defaults.

## Tests and FAQ

The frozen `tests/test_dependency_cache.py:64–71` writes `test_sub_counter`: it resets the counter, makes two calls to the sub-counter route, and asserts matching counter/subcounter pairs of 1/1 and then 2/2, with status assertions. This is written evidence of an intended repeated-dependency scenario, not an observed passing result or proof of every handler branch. `tests/test_dependency_yield_scope.py` is also preserved, but its mere presence does not establish a universal cache lifetime. No FastAPI test suite or application was executed in this campaign. Existing Engineering Library tests are a separate population.

**Is there a single proven cache for every request?** No. The verified initialization boundary is the selected solver invocation receiving its default `None`, with recursive handoff of the local cache.

**Will the selected endpoint call run when solver errors are present?** No. That call is inside the `not errors` branch, with additional branch restrictions. Earlier exceptions can stop the path too.

**Is every raw endpoint result serialized here?** No. The selected serialization call is in the non-`Response` branch after the ordinary selected endpoint path.

**Does the factory always use the original route view?** No. Its written effective-context condition can select another view for the handler arguments. This does not certify every context-setting caller or runtime binding.

## Verification limits

A lexical AST observer records calls and enclosing if/loop conditions. Separate queries reacquire exact public Git objects and check selected imports, arguments, defaults, branches and conservative binding counts. Those queries do not establish complete control flow, arbitrary prose truth, dynamic monkey-patching behavior or full integration. Incorrect synthetic source shapes are development controls, not independent evaluation projects. This isolated chapter awaits completed review; publication, active catalog integration, owner approval and training gold remain false.
