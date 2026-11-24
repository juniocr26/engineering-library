# Config casting diagnostic — after revision

At `271c277da0ff64e2048a4d46ecc812b9d61db5f6`, the selected `Config._perform_cast` handler still catches `TypeError` and `ValueError` from `cast(value)`. It now assigns `cast_name = getattr(cast, "__name__", type(cast).__name__)` and uses `cast_name` in its error message.

Evidence: `starlette/config.py:139–143`. The default expression names the callable's type when the ordinary attribute lookup has no `__name__`. This does not establish that every custom attribute lookup or diagnostic construction succeeds. The selected method's preceding AST, call expression and caught exception types are unchanged. No runtime execution was performed.
