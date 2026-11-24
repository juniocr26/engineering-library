# FastAPI: dependency cache and solver boundaries

Isolated research candidate. Author source review only; separate verification and owner review pending. No publication or training approval.

fastapi/fastapi @ `05e6df7e906c3decba377c37548019973f40bf15`. This chapter covers the selected contract, not the full repository. Evidence: `source-freeze-v1.json`; criteria: `acceptance-protocol-v1.json`.

## Architecture and behavior

**F01** — Dependant stores nested dependencies and defaults use_cache to True; its scope can be function, request or None. [F01: `fastapi/dependencies/models.py:35-56`]

**F02** — _get_cache_key includes the callable, conditional normalized OAuth scopes and computed dependency scope; it is not simply a function-name key. [F02: `fastapi/dependencies/models.py:87-101`]

**F03** — solve_dependencies requires request and function AsyncExitStack objects in request.scope; when no dependency_cache is supplied, it creates a dictionary. [F03: `fastapi/dependencies/utils.py:686-703`]

**F04** — The solver can reconstruct a dependant for an override and recursively passes the same dependency_cache into dependency solving. [F04: `fastapi/dependencies/utils.py:708-736`]

**F05** — After dependency errors are collected, that dependency is skipped; otherwise a cached value is reused only when use_cache is true and the key exists. A missing key is populated after computation even when use_cache is false. [F05: `fastapi/dependencies/utils.py:738-775`]

**F06** — Generator dependencies use an exit stack, coroutine callables are awaited, and other callables run through run_in_threadpool; the selected branches include optional concurrency limits. [F06: `fastapi/dependencies/utils.py:748-771`]

## Example

Synthetic usage fragment, not executed. Resolve dependencies in a separately authorized environment before running. No startup or installer command is authorized here.

```python
from fastapi import Depends, FastAPI
app = FastAPI()
async def counter():
    return 1
@app.get("/sample")
async def sample(value: int = Depends(counter, use_cache=False)):
    return {"value": value}
```

## Test evidence and limitations

`tests/test_dependency_cache.py` is preserved as written test evidence. No external suite, example, dependency installer or runtime was executed. Written assertions are not passing results. No benchmark, concurrency guarantee or release-wide API compatibility is established.

## FAQ

### Q001 — Does use_cache=False prevent every cache write?

After dependency errors are collected, that dependency is skipped; otherwise a cached value is reused only when use_cache is true and the key exists. A missing key is populated after computation even when use_cache is false. [F05]

### Q002 — Is the cache key just a function name?

_get_cache_key includes the callable, conditional normalized OAuth scopes and computed dependency scope; it is not simply a function-name key. [F02]

### Q003 — Does static inspection prove a global cache?

The selected source does not establish global cache lifetime. solve_dependencies requires request and function AsyncExitStack objects in request.scope; when no dependency_cache is supplied, it creates a dictionary. [F03]

## Maintenance and rights

This shallow clone has no local HEAD parent. A historical MODIFY decision is INCONCLUSIVE without a verified earlier source and matching documentation. Missing symbols in this selected scope do not authorize REMOVE. Existing project documentation remains unchanged.

MIT / LICENSE. Notices are preserved with the source snapshot. This artifact is evaluation-only, excluded from training and not owner-approved.
