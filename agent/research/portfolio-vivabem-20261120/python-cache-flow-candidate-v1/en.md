# FastAPI dependency-cache data flow

Isolated source-verified research candidate; owner review, publication and training approval are pending.

## Scope and architecture

Pinned source: fastapi/fastapi @ 05e6df7e906c3decba377c37548019973f40bf15. This chapter follows the selected Dependant declarations and six written cache-flow/assertion rules in solve_dependencies. It connects the model declaration, solver loop, recursive passage, reuse guard and later write guard. It does not document all FastAPI architecture, an installed release or observed service behavior.

## Declarations, flow and error boundaries

### PF01

The written Dependant class declares use_cache: bool = True and a scope field whose declared value is None. This records the selected class statements; it is not observation of a live dependency object.

Evidence: `fastapi/dependencies/models.py:53-53`, `fastapi/dependencies/models.py:55-55`.

### PF02

At the initialization branch, dependency_cache is None guards assignment of an empty dictionary to dependency_cache. The selected function has no other direct assignment to that local name. This does not establish process-wide or cross-request cache lifetime.

Evidence: `fastapi/dependencies/utils.py:700-701`.

### PF03

Inside the selected loop over dependant.dependencies, the written awaited solve_dependencies call passes dependency_cache=dependency_cache. This connects the local cache variable to subdependency solving in the written data flow; dynamic bindings and actual completion remain unverified.

Evidence: `fastapi/dependencies/utils.py:726-737`.

### PF04

The selected reuse branch requires sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache. Its body assigns solved = dependency_cache[sub_dependant_cache_key]. The conjunction is a read/reuse condition; it is not a guarantee that every dependency executes exactly once.

Evidence: `fastapi/dependencies/utils.py:746-746`, `fastapi/dependencies/utils.py:747-747`.

### PF05

When control reaches the later write guard and the key is absent, the written body assigns dependency_cache[sub_dependant_cache_key] = solved. This guard does not mention use_cache. Therefore the selected source does not implement use_cache=False as a general ban on cache writes. Earlier errors, exceptions or control flow can prevent reaching this guard.

Evidence: `fastapi/dependencies/utils.py:774-775`.

### PF06

The selected function contains two written assertions using isinstance with AsyncExitStack: one for request_astack and one for function_astack. These statements do not prove that assertions are enabled in a deployed interpreter, that request composition satisfies them, or that dependency callbacks cannot raise other exceptions.

Evidence: `fastapi/dependencies/utils.py:687-689`, `fastapi/dependencies/utils.py:691-693`.

## Example and written tests

Synthetic dependency-declaration fragment, not a running service. It follows the written use_cache=False call pattern in tests/test_dependency_cache.py:30-35. Its Python syntax was parsed; imports, dependency resolution, type compatibility and execution were not tested. No route is registered here.

```python
from fastapi import Depends

async def synthetic_value():
    return 1

async def synthetic_endpoint(value: int = Depends(synthetic_value, use_cache=False)):
    return {"value": value}
```

The pinned tests/test_dependency_cache.py contains written assertions for repeated requests, nested dependencies and disabled reuse. These external project tests were not executed. Assertions in a file are not passing results or production acceptance. No installer/startup/test command is certified by this chapter.

## FAQ

### Q001 — Does use_cache=False forbid every cache write?

The selected read condition uses use_cache, but the later write guard does not. If execution reaches that guard with an absent key, the written assignment stores solved. This is a source-level distinction, not an observation that every invocation succeeds. [PF04, PF05]

### Q002 — Is a global cache lifetime established?

No global lifetime is established by this profile. It observes initialization when the local value is None and passage of the same local name to the written recursive call. Caller composition, external aliases and actual reuse across requests require separate evidence. [PF02, PF03]

### Q003 — Does this prove exactly-once dependency execution?

No. The rules describe selected cache data flow and guards. They do not establish callback completion, concurrent invocation counts, effective cache-key equivalence or live override behavior. Written test assertions are separate from executed results. [PF03, PF04, PF05]

### Q004 — Do the stack assertions establish complete error handling?

No. They are two specific written assertions. This profile does not establish interpreter assertion settings, caller correctness, callback exception translation, cleanup completion or every possible error path. [PF06]

## Unresolved context and preservation

This closed profile does not reconstruct cache-key construction, override resolution, effective generator scopes, concurrency limits or complete cleanup behavior. In particular, it does not say keys are merely function names. Those contracts need their own evidence. Source syntax, fixed text and exact quotations do not prove arbitrary prose truth or runtime integration.

The frozen inventory recorded a shallow clone with no local parent revision. No historical MODIFY decision is inferred from this one revision. Missing symbols in partial source never authorize REMOVE. Existing project documentation remains unchanged. MIT license notices are retained in the pinned source evidence. This candidate and its source family remain outside training; source verification is not owner-approved gold.
