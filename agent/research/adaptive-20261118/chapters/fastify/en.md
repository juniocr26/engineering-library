# Fastify: hook execution and validation boundaries

Experimental chapter authored by Codex after source review. This is a correction draft, not unchanged local-model output. Human factual and bilingual approval is pending; it is not a positive training answer.

Source revision: `825d7722e4932a39193729997c76535d0a963b6b`.

## 1. Hook names index arrays of handlers

`Hooks` initializes arrays such as `onRequest`, `preValidation`, `onReady`, `onListen` and `preClose`. These fields store handler lists; the assignments do not define methods with those names. This constructor creates empty lists and does not invoke a handler. [lib/hooks.js:40–56](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L40-L56)

`Hooks.prototype.validate` checks a string hook name, an array at `this[hook]`, and a function-valued handler, with the corresponding explicit throws. `Hooks.prototype.add` calls that validation and executes `this[hook].push(fn)`. It appends the handler, not a second hook/handler pair or a copy of the whole registry. [lib/hooks.js:60–66](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L60-L66), [lib/hooks.js:68–71](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L68-L71)

`buildHooks` constructs `new Hooks()` and copies the listed inherited arrays using `slice()`. It then assigns new empty arrays to `onReady`, `onListen` and `preClose`. The copied arrays are distinct containers, while the source contains no deep-cloning of their function entries. The three reset lists must not be described as inherited handlers. [lib/hooks.js:73–91](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L73-L91)

## 2. Dispatch goes through the supplied iterator

`hookRunnerGenerator` returns a runner with index `i = 0` and starts it through `next()`. In `next(err)`, an error or exhaustion calls `cb(err, request, reply)` and returns. Otherwise it invokes `iterator(functions[i++], request, reply, next)` inside a try block. The direct callee is the supplied iterator, so the body alone does not establish how that iterator invokes a hook or which arguments it supplies to it. [lib/hooks.js:230–266](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L230-L266)

The same runner catches a synchronous iterator throw and calls `cb(error, request, reply)`. A truthy result with a function-valued `then` receives `handleResolve` and `handleReject`. Resolution calls `next()`; rejection replaces a falsy error with `new FST_ERR_SEND_UNDEFINED_ERR()` and calls `cb`. For a result outside that thenable branch, this body makes no additional automatic advance: the supplied iterator has received the continuation. [lib/hooks.js:230–266](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L230-L266)

## 3. Application hooks combine registration, children and completion

`hookRunnerApplication` tracks its own hooks with `i` and child instances with `c`. It registers `boot(wrap(hooks[i++], server))` and calls `next()`. After its own list is exhausted, it recursively visits children through `hookRunnerApplication(hookName, boot, child, next)`. The supplied body exposes registration and traversal order; execution scheduling remains inside the external boot mechanism. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

When both lists are exhausted, the no-hook/no-child case calls `exit()` directly. Otherwise a registered `manageTimeout(err, done)` body calls `exit(err)` before `done(err)`. The exit path converts `AVV_ERR_READY_TIMEOUT` through `FST_ERR_HOOK_TIMEOUT`; other mapped error codes use `AVVIO_ERRORS_MAP` and `appendStackTrace`. It calls `cb(err)` for the error path or `cb()` for the other path. The map and conversion calls occur in this cited function, not only in its final fragment. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

The wrapper first forwards an incoming error to `done(err)`. For `fn.length === 1`, the written call is `fn.call(server, done)`: the call form supplies the server as receiver and the completion function as an argument. Other functions use `fn.call(server)`. A returned thenable receives `ret.then(done, done)`; a synchronous throw is assigned to `err`, and the remaining path calls `done(err)`. This source does not pass the server as an ordinary positional argument to the hook. [lib/hooks.js:93–181](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L93-L181)

## 4. Listen hooks use a continuation, not the wrapper promise as coordinator

`onListenHookRunner` captures the hook count, starts `next()` and logs a truthy error through `server.log.error(err)`. When its own hooks are exhausted, it iterates over the children and calls `onListenHookRunner(child)`. Otherwise it calls `wrap(hooks[i++], server, next)`. The outer function has no return statement that exposes the async wrapper result to its caller. [lib/hooks.js:183–228](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L183-L228)

The nested `async function wrap` uses the callback-style path for `fn.length === 1`, calling `fn.call(server, done)` inside a try/catch and returning afterward. That branch does not await a returned value. The other path calls `fn.call(server)`, attaches `ret.then(done, done)` to a thenable and otherwise calls `done()`. Synchronous errors are forwarded to `done(error)`. Merely declaring the wrapper async does not make the callback-style branch wait for its completion callback. [lib/hooks.js:183–228](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/hooks.js#L183-L228)

## 5. Parameter validation has different synchronous and thenable paths

`validateParam` returns `false` when `validatorFunction == null`, before reading `request[paramName]`. Otherwise it reads that request part and converts only `undefined` to `null` for the data argument. A truthy `validatorFunction.schemaEnv` selects the call with `parentData: request` and `parentDataProperty: paramName`; the other call receives only the data. The schema environment selects a call form; it is not passed as the schema argument. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

A synchronous throw inside the shown validation try block assigns `err.statusCode = 500` and returns `err`. This is a returned error object at this boundary. The catch does not justify an exception-free guarantee for every later getter, thenable implementation or caller interaction. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

For a truthy result with a function-valued `then`, the returned chain maps `res === false` to `validatorFunction.errors` and every other resolution value to `false`. Its rejection handler returns `err`. This branch does not unwrap the resolved payload through the synchronous answer function: payload properties named `error` or `value` are not used here to replace the request part or inject a validation result. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

The synchronous `answer(ret)` path first maps `ret === false` to `validatorFunction.errors`. A truthy `ret.error` is returned next. Only after those guards does an object satisfying `'value' in ret` assign `request[paramName] = ret.value`; the final return is `false`. The membership test includes inherited properties and does not require an own-property check. Other falsy values are not automatically validation errors. [lib/validation.js:354–396](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L354-L396)

## 6. Error wrapping preserves some fields and overwrites others

`wrapValidationError` first tests `result instanceof Error`. In that branch it keeps truthy existing fields and otherwise supplies `statusCode` with `400`, `code` with `FST_ERR_VALIDATION` and `validationContext` with `dataVar`, then returns the same object. The fallback operator is logical OR, so this is not limited to null or undefined fields. This branch does not add a new validation payload assignment. [lib/validation.js:508–522](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L508-L522)

The other branch calls `schemaErrorFormatter(result, dataVar)` with two arguments. It applies the same status/code fallbacks, then assigns `error.validation = result` and `error.validationContext = dataVar` before returning `error`. The context assignment here overwrites an existing value. The supplied code does not read status or code from the context label, and it does not establish the formatter implementation or guaranteed successful return. [lib/validation.js:508–522](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L508-L522)

## 7. Validation order, skip flags and the false sentinel

`validate` sets `runExecution = execution === undefined`. Its initial fast path returns `false` only when this is true and all four selected schema slots are `undefined`. The subsequent order is params, body, query and headers. The first three stages honor `execution.skipParams`, `execution.skipBody` and `execution.skipQuery` when not starting a new execution; the headers stage has no corresponding skip flag in this body. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

For body validation, a function at `context[bodySchema]` is used directly. Otherwise a truthy schema container is indexed by `request.mediaType`; only a truthy matching entry replaces the initially null validator. This function does not parse a content-type header, normalize its case or invent a schema for an unmatched media type. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

Each stage calls `validateParam` and inspects a truthy result. A result without a function-valued `then` is passed to `wrapValidationError`; a thenable result is passed to the stage-specific async helper and returned. The helper bodies are not supplied here. Query data is read through `query`, while its error-context label is `querystring`. The final `false` marks the path that found no truthy validation result; it is not an unconditional failure signal. [lib/validation.js:398–462](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/lib/validation.js#L398-L462)

## Evidence and limits

The cited definitions were inspected statically. No upstream application, database, server or test suite was executed to establish runtime behavior. External helpers need their own source and assumptions. These chapters expand and correct research drafts; they have not been placed in the public catalog. Source licenses and exact quotations/hashes are retained in the campaign evidence.

Source project license: [LICENSE](https://github.com/fastify/fastify/blob/825d7722e4932a39193729997c76535d0a963b6b/LICENSE). The exact license text and its checksum are retained with the source evidence.
