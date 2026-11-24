# Server error middleware: protocol delegation, response state and propagation

Codex-authored source-reviewed correction; pending owner approval.

Starlette revision 271c277da0ff64e2048a4d46ecc812b9d61db5f6; actual preserved baseline: starlette-server-error-contract. [Exact source excerpts](../references/ref-4545e1191a9e3290414a.md).

## The non-HTTP branch still calls the application

The actual local-agent baseline claimed that this middleware is only called for HTTP. The selected method shows a different boundary: when `scope["type"] != "http"`, it awaits `self.app(scope, receive, send)` and returns. The middleware can therefore be invoked for another scope type and delegate it. That application call is outside the later HTTP try block and uses the original send callable.

For HTTP, the method creates a local `response_started` flag, initially false, and defines a wrapped sender. It then awaits `self.app(scope, receive, _send)` inside the try. These are distinct paths, rather than one universal call using the wrapper. If the HTTP application completes normally, the method has no written response-object return; its declared result is None. A protocol gate must not be confused with an assertion that the object can never receive a non-HTTP scope.

## The start flag records a message path, not wire delivery

The wrapper checks `message["type"] == "http.response.start"`. When that comparison succeeds, it sets `response_started` to true before awaiting the original `send(message)`. The flag is captured with nonlocal for this invocation. It is not a count of bytes delivered, a confirmation from a client or a verified network response status.

That ordering matters when the original sender itself fails: the local marker has already been set before that awaited call completes. The selected body does not validate every ASGI message sequence or establish that a start message reached the network. It uses this local marker later to decide whether to invoke the generated error response. The baseline noticed a start flag at a high level, but its Portuguese text changed the source identifier. This correction keeps `response_started` unchanged in both languages.

## Debug, default and custom handling have an order

The HTTP error branch is `except Exception as exc`. It constructs `Request(scope)`, then selects a response. A truthy `self.debug` takes precedence and awaits `run_in_threadpool(self.debug_response, request, exc)`. Otherwise, `self.handler is None` selects the synchronous default `error_response` call. A configured custom handler reaches the separate `is_async_callable` predicate.

When that predicate succeeds, the custom handler is awaited directly with request and exc. Otherwise it is passed to `run_in_threadpool` with those arguments. This does not mean the method invokes both forms or always invokes a configured custom handler in debug mode. The constructor excerpt stores app, handler and debug, with handler defaulting to None and debug to false; these annotations and assignments are not runtime validation of every possible configured object.

## Supplied helpers explain delegation without proving runtime scheduling

The manually expanded `run_in_threadpool` body binds the callable and arguments with `functools.partial`, then returns the awaited result of `anyio.to_thread.run_sync(func)`. The source shows result propagation through that helper. It does not provide a runtime observation of a particular worker thread, cancellation policy or application completion.

The supplied `is_async_callable` implementation repeatedly unwraps `functools.partial` objects. It then tests `iscoroutinefunction` on the object or, if callable, on its `__call__` member. This is the written predicate, not a universal classifier of every object that might return an awaitable. The response-builder excerpts are also concrete: `error_response` constructs `PlainTextResponse` with the literal `Internal Server Error` and status 500; `debug_response` chooses HTML when the accept header contains `text/html`, otherwise plain text, with status 500 in both written branches. Their formatting helpers were not expanded into a promise about escaping or traceback content.

## Building a response and sending it are different decisions

The response-selection block runs before the check of `response_started`. Thus even when a response has already started according to the local marker, this body still selects and constructs its error response, subject to normal helper completion. Only the later `if not response_started` branch awaits `response(scope, receive, send)`, using the original sender. Saying that the handler is never called after a start event would overstate this guard.

After those operations complete, the explicit `raise exc` propagates the caught exception. The error is not silently swallowed merely because a response was sent. If a handler or response invocation raises first, the final statement may not be reached; the body has no finally forcing that original raise after every possible helper failure. This correction preserves the distinction between error-response work, sending and propagation. It reuses the original completed baseline without another model request and remains pending owner review, with exact source and notices retained, no publication and no training approval.

## Engineer FAQ

<!-- reading-section: faq:debug-handler-precedence -->
### Does debug mode also invoke the configured error handler?

The debug branch precedes the custom-handler selection. When debug is truthy and its helper completes normally, this source selects the debug response instead. A configured custom handler is not called by that selection path.

<!-- reading-section: faq:response-start-not-delivery-proof -->
### Is a response-start message proof that the client received headers?

The local flag is set before the original sender is awaited. A sender failure can therefore occur after the flag changes. The flag controls the later error-response invocation; it is not a delivery acknowledgment.

<!-- reading-section: faq:original-exception-rethrow -->
### Is the original exception swallowed after a generated response?

The final written operation raises the caught exception after prior selected operations complete. A handler or response failure can prevent reaching that line, because no finally forces it. The separate non-HTTP delegation is outside this HTTP catch block.

The selected constructor accepts the application, optional handler and debug flag. This chapter has not verified server configuration, persistence, retry, authentication or an actual ASGI deployment; those responsibilities require their own source and runtime evidence.
