# Config cast diagnostic — preceding revision

At `9b403a0c33f0e2eebba099e9e6aa1c1e9535daec`, the selected `Config._perform_cast` handler catches `TypeError` and `ValueError` from `cast(value)` and builds its diagnostic using `cast.__name__` directly. Evidence: `starlette/config.py:139–142`.

A later bounded campaign observation executed only a copy of this method body, with annotations stripped and known builtin bindings. An owned `OwnedInvalidCallable` instance raised `ValueError` from its call and had no `__name__`; the copied preceding body then raised `AttributeError` while constructing its diagnostic. This is an observed result for that owned case, not a statement that every failing cast raises that exception.

No Starlette module import, `Config` construction, configuration/environment-file access by the inspected method or upstream test suite was performed. This source/body observation is not complete application integration, owner approval or training gold.
