# Prefix trailing slash handling: explicit and generated HEAD

At Fastify revision `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3`, the selected `buildRouting.route` branch enters the `prefixTrailingSlash` switch when `path === '/' && prefix.length > 0 && !opts.isGeneratedHeadRoute`. The previous revision `0b076ca595d19951c536daf515c778b38cf6ba69` instead tested `opts.method !== 'HEAD'` as the third conjunct. The path and prefix prerequisites remain. Evidence: new `lib/route.js:250–274`, old `:250–273`.

Consequently, when `opts.method` is exactly the string `HEAD` and the generated marker is false, the method comparison that previously excluded it is no longer present in that guard. This is a statement about the written condition, assuming earlier control reaches it; it does not guarantee successful registration for every possible input.

The local marker comes from `opts.isGeneratedHeadRoute = isFastify === true` after the options copy (`lib/route.js:206–213`). In the examined generated-HEAD path, `shouldExposeHead && isGetRoute && !isHeadRoute && !hasHEADHandler` guards a `prepareRoute.call` carrying `method: 'HEAD'` and `isFastify: true` (`:457–459`). `prepareRoute` later forwards `isFastify` to `route.call` (`:143–170`). These selected links explain the marker distinction; they do not exhaust every API caller.

The switch body and subsequent else branch are textually unchanged in this revision. The `slash` case passes `path`; `no-slash` passes an empty path. The `both`/default case first adds the empty path and adds the other path only under `ignoreTrailingSlash !== true && (ignoreDuplicateSlashes !== true || !prefix.endsWith('/'))`. If the outer switch guard is false, the subsequent branch may strip one leading slash when `path[0] === '/' && prefix.endsWith('/')`; otherwise it passes `path`. Evidence: new `lib/route.js:254–274`.

With owned inputs `path = '/'`, `prefix = '/p'` and a false generated marker, the old copied expression returned false for `opts.method = 'HEAD'` but true for `opts.method = ['HEAD']`. The revised copied expression returned true for both. An array containing a method is not strictly equal to that string. The surrounding source also has an `Array.isArray(opts.method)` branch (`lib/route.js:231–245`); this observation does not prove normalization, complete registration or reachability of every synthetic input combination.

Sixteen evaluations of the two copied Boolean expressions matched their frozen eight-case reference under the existing Node/TypeScript runtime. Exact source hashes, lexical owner and an operator/literal/property AST whitelist were checked before evaluation. The original module was parsed as text and never imported or executed. These are owned expression observations, not sixteen upstream tests.

## FAQ

**Are all HEAD routes now handled identically?** No. The selected condition distinguishes the generated marker, while retaining path/prefix prerequisites and later branch conditions.

**Does a generated marker alone prove registration succeeds?** No. Earlier validation, later calls and runtime behavior are outside this static result.

**Was the Fastify application or its upstream test suite executed?** No. Only the two reviewed copied Boolean expressions were evaluated on owned plain inputs. Module import, construction, startup, integration, configuration/data access by the inspected expressions and upstream tests were not performed. The observer reads retained source evidence and writes research receipts.

This isolated candidate is ready for owner review only. It is not owner approved, training gold, an independent holdout score or an operational catalog update.

Additional evidence: `fastify-method-shape-guard-protocol-v1.json`, `fastify-method-shape-guard-review-v1.json` and `fastify-method-shape-guard-stdout-v1.json`. Earlier static-only candidate and Boolean abstraction remain preserved.
