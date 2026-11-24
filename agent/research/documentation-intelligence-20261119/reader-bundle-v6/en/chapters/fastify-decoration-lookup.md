# Fastify decoration lookup: ordered guards and an explicit fallback

Codex-authored experimental correction reviewed against frozen source, pending human approval. Source: Fastify revision `825d7722e4932a39193729997c76535d0a963b6b`, `lib/decorate.js`. The actual local-agent baseline is `fastify-checkrequestexistence`. It contained only the request wrapper. This chapter explicitly expands the evidence to the reply wrapper, shared helpers, import names and export aliases from the same file. No Fastify module, HTTP server or inspected application source was executed.

## The wrapper tests a supplied name

The function `checkRequestExistence` accepts a parameter named `name`. Its first condition is `name && hasKey(this[kRequest], name)`. A truthy result reaches the written return expression `true`. Only when that branch is not taken does the function reach the second condition, `name && hasInstanceProperty(this[kRequest], name)`. That branch also returns the written true expression when its condition is truthy.

The name participates in both short-circuit conditions. A falsy name prevents the corresponding helper operand from being evaluated in either guard. That observation does not determine the function's eventual result: there is still a final statement. It returns `checkExistence(this[kRequest].prototype, name)`. The wrapper has no unconditional false-return statement for an omitted name. The neural baseline invented exactly that fallback.

The bracketed access is also part of the parameter-role distinction. The source does not pass a request object as the explicit argument to this function. It obtains a target through a property of the runtime receiver and passes the supplied name to helpers. The imported key's value and the actual receiver must not be inferred merely from the function's name.

## The reply path is a sibling contract

The function `checkReplyExistence` has the same sequence using `this[kReply]`. Its final call targets the corresponding prototype. This is useful corroboration of the written pattern, but it is one related decoration-lookup family. Two similarly shaped wrappers do not establish independent transfer or prove how every caller binds their receiver.

The file obtains the two key names through a relative import and exports the wrappers under `existRequest` and `existReply`. These are explicit source relationships. The export aliases do not prove that a server has registered or invoked the functions in a particular runtime. This inspection neither loads the imported module nor creates requests or replies.

## The two early helpers inspect different structures

The helper `hasKey` checks the truthiness of a `props` property. When present, it calls that property's array-style search operation with a predicate comparing a stored key with the supplied name; otherwise, the written alternative result is false. The source does not validate that the property has every expected runtime method, and a property access or called operation is not automatically free of effects.

The helper `hasInstanceProperty` begins with a local cursor set to its first argument. While the cursor is truthy, it tests a property collection and its membership operation. A successful condition returns true. Otherwise, it assigns `k = k.parent` and continues; exiting the loop reaches false. This is a specific parent-field traversal. It is not interchangeable with automatically traversing JavaScript prototypes, and the body does not demonstrate cycle detection or guaranteed termination for arbitrary objects.

## The final helper does not justify a missing-name false result

The helper `checkExistence` distinguishes a truthy name from the other path. For a truthy name, it combines membership tests and a call to the stored-key helper. For the other path, the written expression is `instance in this`. That expression is not a constant false. Receiver validity and the point reached remain explicit preconditions.

If this branch is reached through the shown plain strict-mode call, `this` is `undefined`; applying `in` with that right operand raises `TypeError`. This is a conditional language-derived path, corroborated by an owned synthetic probe, not an observed Fastify execution. The language rules are specified by [strict this binding](https://tc39.es/ecma262/2026/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinarycallbindthis) and [relational-operator evaluation](https://tc39.es/ecma262/2026/multipage/ecmascript-language-expressions.html#sec-relational-operators-runtime-semantics-evaluation).

The wrappers perform no explicit assignment to the target request/reply structure in their own bodies. This does not prove global purity: helper calls, getters and runtime object behavior remain separate dependencies. The correction therefore preserves the order and exact fallback while keeping those boundaries visible.

The standalone source producer now adds an optional ordered-guard packet for these wrappers. Its original first-guard paragraph is unchanged, and its new packet records written expressions rather than supplying missing helper semantics. The actual model baseline remains rejected; this chapter and the deterministic packet are separate artifacts, without neural training, publication or automatic promotion to approved training data.

## Public API wiring and declared identifier types

The frozen `fastify.js` imports `./lib/decorate` and assigns `hasRequestDecorator: decorator.existRequest` in the instance object. The export in `lib/decorate.js` connects that property value to `checkRequestExistence`. This is a concrete source-level consumer relationship, not a claim that every possible call preserves its receiver.

The `FastifyInstance` interface in `types/instance.d.ts` declares `hasRequestDecorator(decorator: string | symbol): boolean`. It declares a required identifier argument and a Boolean result on normal completion; a declaration does not prove that every runtime input returns normally. The implementation parameter `name` is that supplied identifier. By contrast, `kRequest: Symbol('fastify.Request')` in `lib/symbols.js` declares an internal target-selection key. The two roles must not be merged merely because either identifier can involve a symbol.

The instance object also initializes `[kRequest]: Request.buildRequest(Request, options.trustProxy)`. This establishes the visible factory delegation and configuration argument. The factory body was not inspected for this supplement, so its output construction, proxy behavior and execution effects remain outside the verified claim. No authentication, persistence, timeout or retry policy follows from the lookup's name or this call alone.

## FAQ

<!-- reading-section: faq:omitted-identifier-guard -->
### Does an omitted identifier always return false?

No. The declared public interface requires an identifier. The wrapper's source has a final helper call even when the early conditions are falsy, and the conditional strict-call error path is described above. That is not a recommendation to rely on undocumented inputs or proof of an executed Fastify failure.

<!-- reading-section: faq:internal-key-identity -->
### Is the internal key the decoration name?

No. The internal key selects a target from the receiver; the explicit argument identifies the decoration to inspect within the selected structure. The source-level distinction remains important even when the caller supplies a symbol.

<!-- reading-section: faq:helper-receiver-binding -->
### Does preserving the outer receiver bind every helper?

No. A method property supplies a function value, while each call expression determines its own receiver. Binding the outer wrapper does not automatically bind a plain nested helper call. The chapter's conditional error explanation preserves that boundary; it does not claim that all lookups throw.

This supplement adds interface and wiring evidence, not a production change or an independently executed application example. The original candidate, baseline response and source evidence remain preserved for owner review.
