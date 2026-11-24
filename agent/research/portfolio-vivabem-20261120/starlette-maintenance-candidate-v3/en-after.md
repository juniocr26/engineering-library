# Config cast diagnostic — revised version

At `271c277da0ff64e2048a4d46ecc812b9d61db5f6`, the selected `Config._perform_cast` handler still catches `TypeError` and `ValueError` from `cast(value)`. It assigns `cast_name = getattr(cast, "__name__", type(cast).__name__)` and uses `cast_name` in the diagnostic. The preceding selected-method AST, cast call and caught exception tuple are unchanged. Evidence: `starlette/config.py:139–143` and the pinned real revision diff.

The default expression names the callable's type when ordinary attribute lookup lacks `__name__`. It does not make every custom attribute lookup safe, and Python evaluates the default argument expression before calling `getattr`.

In the bounded owned case, an `OwnedInvalidCallable` instance raised `ValueError` from its call and had no `__name__`. The copied revised body raised `ValueError` with a diagnostic naming `OwnedInvalidCallable`; the preceding copy raised `AttributeError`. Another owned object's `__name__` lookup raised `RuntimeError`, which was observed in both copies. Thus the observed improvement is specific; a universal successful-diagnostic guarantee remains unsupported.

All 12 owned cases were evaluated against both copied bodies under known bindings: 24 observations per context. Typed values/exception messages matched between Darwin ARM64 Python 3.14.7 and the existing Linux ARM64 Python 3.11.2 container. These are repeated, correlated body observations, not 48 independent project tests. No original module import, `Config` construction, configuration/environment-file access by the inspected method or upstream test suite was performed. Full module bindings, Windows and application integration remain unverified.

Evidence: `starlette-cast-bounded-runtime-protocol-v1.json`, `starlette-cast-bounded-runtime-observation-v1.json` and `starlette-cast-cross-context-review-v1.json`. This isolated maintenance candidate is ready for owner review only; it is not owner approved, training gold or an active catalog update.

The owned observer necessarily reads retained source evidence and writes research receipts. The no-file-access limit above refers to application configuration/data access by the selected method, not to the observer’s evidence I/O.
