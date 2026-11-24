# Fastify: route registration, prefixes and generated HEAD

This chapter describes selected source at Fastify revision `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3`. It is a historical revision, not a claim about the collection's newer checkout. The topic is registration context around the root-prefix guard, not the complete request pipeline or router implementation. This is a manually authored source-first research candidate, not neural learning, owner approval or a training record. Fastify's pinned `LICENSE` is retained with the evidence.

## Entry points and ownership

In `fastify.js:197-231`, public shorthand methods call `router.prepareRoute.call`; the HEAD shorthand supplies scalar `HEAD`, while `all` supplies `this.supportedMethods`. The extended route entry calls `router.route.call` with an options object. These selected public entries do not supply the internal `isFastify` argument. The connection is written across files: `fastify.js:51,116` imports and invokes `buildRouting`, and `lib/route.js:93-126,726` returns the registration functions and exports the builder. The routing-library instance inside that builder is a different local `router` from the object returned to `fastify.js`.

The lexical observer can locate local declarations, including `prepareRoute` calling `route` and `addNewRoute` calling `prepareRoute`. It leaves property calls such as `router.on` unresolved. Cross-file wiring was reviewed manually; it was not inferred automatically by that observer. Neither a lexical binding nor a `.call` expression proves the runtime target cannot be replaced.

## Options, normalization and early errors

In `lib/route.js:143-170`, `prepareRoute` checks the URL and selected options/handler combinations. It copies options with `Object.assign`, then supplies `method`, `url`, `path` and the selected handler. The copied method argument therefore takes precedence over an options property on this path. It forwards the separate `isFastify` argument to `route`.

At `lib/route.js:206-245`, `route` first checks whether registration is already started, shallow-copies options into `opts`, and assigns `opts.isGeneratedHeadRoute = isFastify === true`. Supplying an options property with that name does not bypass the assignment on the selected public path. Missing handlers, an invalid custom error handler, body-limit validation and handler-timeout validation can interrupt registration before method processing or prefix branching. This chapter does not enumerate every validation rule or every later error.

For a scalar method, `normalizeAndValidateMethod` requires a string, uppercases it and checks the two supported-method sets (`lib/route.js:637-647`). Invalid type and unsupported method use `FST_ERR_ROUTE_METHOD_INVALID` and `FST_ERR_ROUTE_METHOD_NOT_SUPPORTED`. `validateSchemaBodyOption` rejects a body schema for a method in the bodyless set (`lib/route.js:650-653`); these sets are dependencies, not an exhaustive method list established here.

For an array, the same normalization and schema validation occur for each indexed element. The array remains an array: a one-element HEAD array is not collapsed into a scalar. Indexed assignments also matter for ownership: the shallow options copy retains the original method-array reference, so this code can change its elements. An empty array skips the loop; that observation does not guarantee successful downstream registration. Exceptions or unsupported input stop the selected path before its later decisions.

## Root prefixes and generated routes

The local `shouldExposeHead` uses the per-route `exposeHeadRoute` option when it is not nullish, otherwise the builder's `globalExposeHeadRoutes`; setup assigns that global from `options.exposeHeadRoutes` (`lib/route.js:98-109,226`). Detection of GET and HEAD uses normalized scalar equality or array membership. When exposure is enabled and a GET is detected, `headOpts` is a shallow copy of the original options (`lib/route.js:247-248`), not a deep copy of all mutable nested state.

At `lib/route.js:250-274`, a root path with a nonempty prefix enters the slash-selection branch only when the generated-route flag is false. Explicit public HEAD registrations can therefore enter it, whether their method is scalar or an array. `prefixTrailingSlash` selects a slash form, a no-slash form or the default both-form path. In the both case, the second local registration is additionally guarded by `ignoreTrailingSlash`, `ignoreDuplicateSlashes` and whether the prefix already ends in a slash. Other paths have a separate prefix-ending-slash adjustment. The source does not say every prefix produces two registrations.

Within `addNewRoute`, URL/path fields are updated and non-prefixing registration runs `onRoute` hooks before `router.on` (`lib/route.js:279-303,365`). Those callbacks receive `opts`; their effects and the external router's behavior are outside this selected lexical proof. The flags computed earlier must not be treated as a guarantee that arbitrary callbacks leave every option unchanged. The router insertion catch also distinguishes generated-route context when deciding whether to rethrow (`lib/route.js:366-377`); this is not a guarantee that all registration errors are swallowed.

The selected automatic HEAD construction is conditional on exposure enabled, GET present, HEAD absent and no already found HEAD handler (`lib/route.js:361-362,457-459`). It calls `prepareRoute` with scalar `HEAD`, the local path, prepared send handlers and `isFastify: true`. That selected recursive route receives the generated flag and skips the root-prefix split. It does not construct an array method. This is a statement about the selected construction site, not a global impossibility claim about dynamically modified JavaScript.

## Illustrative registration fragment

Given an appropriately initialized Fastify instance as `app`, this fragment declares an explicit HEAD-array route under a prefix. It does not invoke the function, start a server or demonstrate actual response bytes. It illustrates an explicit registration, not the internal automatic HEAD API.

```js
function defineRoutes(app) {
  app.register(function prefixed(scope, _options, done) {
    scope.route({
      method: ['HEAD'],
      url: '/',
      handler(_request, reply) { reply.send(); }
    });
    done();
  }, { prefix: '/api' });
}
```

Only the fragment's syntax is checked in this research work. Package typing, plugin lifecycle, route insertion and network behavior are not executed. The source trace explains why the method-array shape survives selected normalization and why public options alone do not mark this as generated.

## Written tests and evidence limits

The selected `test/route-prefix.test.js:395-425` contains assertions for GET on both prefixed forms. The selected `test/http-methods/head.test.js:110-126` registers `['HEAD', 'GET']`; its corresponding HTTP fetch assertions are at lines 254-262 in that file. These are written test evidence, not tests run in this campaign, and the two cases do not establish every combination of explicit HEAD, array methods, prefix flags and hook mutation. No upstream installation, server startup, migrations or upstream test execution occurred. Existing campaign baseline suite results belong to Engineering Library and cannot be attributed to these upstream tests.

## FAQ

**Does every HEAD method skip the root-prefix branch?** No. The selected branch tests the generated flag. Explicit public HEAD registrations can enter it; the selected automatic construction supplies the internal flag.

**Can an options property alone mark a public route as generated?** No on the selected public path. The separate internal argument controls the assignment, which overwrites that options property.

**Does an array become a scalar after normalization?** No. The selected loop replaces each element and retains the array; shallow copying does not isolate that array from the original options.

**Do these sources prove both prefix forms always work?** No. Local slash choices and ignore flags vary, later hooks and router insertion matter, and written tests were not run here.

**Is the observer's local-function reference a runtime call-graph guarantee?** No. It identifies narrow lexical declarations and callback ownership. Properties, aliases, imported bindings and runtime replacement require additional evidence.

## Preservation and uncertainty

The earlier guard-only experiment remains preserved; this chapter adds source context rather than reinterpreting its sixteen Boolean observations as server executions. All source selections, the two actual language files, lexical observations and review receipts are separate research artifacts. External repositories, the active documentation catalog, production code and permanent tests remain unchanged. Development exposure prevents an independent-family evaluation claim. This candidate requires complete bilingual/source review and then owner review; it is not Gold, not published and not authorization to train.
