# Starlette tasks and iteration: call, return, yield and exception boundaries

Codex-authored source-reviewed experimental correction, pending owner approval. Frozen Starlette revision 271c277da0ff64e2048a4d46ecc812b9d61db5f6. Actual local-agent baselines from contract waves 2 and 3 are preserved; no whole baseline response was approved. The correction explicitly combines the two files in [source evidence](source-excerpts.json). No inspected application was executed.

## Preserved call arguments

The constructor of `BackgroundTask` stores the supplied callable, positional argument tuple and keyword mapping on separate fields. It also assigns the result of `is_async_callable(func)` to a field. The helper's implementation is not included in these two selected files, so the correction does not turn that name into a proof about every callable's runtime classification. The constructor shows what is stored and what expression computes the branch flag; it does not execute the stored callback.

The async `__call__` method tests `self.is_async`. On the truthy branch it awaits `self.func(*self.args, **self.kwargs)`. On the other branch it awaits `run_in_threadpool(self.func, *self.args, **self.kwargs)`. These are two written call paths, not evidence that both run or that callbacks run concurrently. There is no explicit return or exception handler in this method. Its annotation and stored inputs do not by themselves establish successful completion or the callback's result type.

## The helper returns an awaited expression

The supplied `run_in_threadpool` body first reassigns its local func parameter with `functools.partial(func, *args, **kwargs)`. It then executes `return await anyio.to_thread.run_sync(func)`. If that awaited expression completes normally, this body returns its result. The earlier local-model answer omitted that return relationship. The deterministic source-fact profile records it without asserting how partial or run_sync implements argument binding, scheduling, cancellation or exception transport.

The imports show where the written helper names come from. They do not supply the imported implementations. In particular, the name `run_in_threadpool` is insufficient evidence for pool size, thread reuse, parallelism or performance. No Starlette callback, AnyIO operation or inspected application was executed during this review. Source facts remain different from measured runtime behavior.

## A task collection awaits its elements in order

`BackgroundTasks` initializes `self.tasks` with `list(tasks)` when the supplied value is truthy and with an empty list otherwise. Its `add_task` method constructs a `BackgroundTask` from the given callable and arguments, then appends that object. The code does not invoke the new task inside `add_task`. The call method iterates `self.tasks` and awaits `task()` for each element reached.

That loop awaits the current operation before advancing through the written loop. It contains no task-group creation, gathering operation or local try/except. An exception escaping an awaited task is not caught by this body, so later iterations are not guaranteed to execute. This does not establish that unrelated system work stops, or that the stored list cannot change through other references. A complete account must keep list construction, appending and eventual invocation separate.

## Iterator exhaustion is translated, then handled by `break`

The file defines `_StopIteration` as a subclass of `Exception` with a `pass` body. The helper `_next` attempts `return next(iterator)`. Its `except StopIteration` handler executes `raise _StopIteration`. This is the shown translation path; there is no handler for every possible error. The written class and helper support a more precise account than inferring all behavior from the iterator wrapper's name, while actual name rebinding and imported implementation behavior remain outside this inspection.

The async generator `iterate_in_threadpool` assigns `iter(iterator)` to `as_iterator` before entering `while True`. Within the loop it tries `yield await anyio.to_thread.run_sync(_next, as_iterator)`. A normally completed awaited result is yielded to the consumer; it is not a final return value. Its `except _StopIteration` handler contains `break`. The neural baseline incorrectly described this outer handler as reraising the exception. The helper raises the translated name; the outer written handler terminates its loop. Those operations belong to different bodies.

The wrapper contains no loop else, try else or finally and does not demonstrate cleanup of an arbitrary underlying iterator. Other errors are not caught by this specific written handler, but the exact runtime exception-matching outcome depends on bindings and execution. There is no source basis for a batching, retry or concurrent-prefetch guarantee. The source-derived profile added in this campaign preserves the initializer, yielded call and `break` without converting unresolved helpers into semantic facts.

This chapter is a corrected research candidate, not a model-weight improvement or approved training answer. The deterministic iteration extension was verified on this actual family and owned controls; independent real-repository transfer is not established.
