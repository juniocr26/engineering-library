# Prefix trailing slash handling: explicit and generated HEAD

At Fastify revision `7e0c8febb2a1ba4d55309cdc2ccd51694eca46d3`, the selected `buildRouting.route` branch enters the `prefixTrailingSlash` switch when `path === '/' && prefix.length > 0 && !opts.isGeneratedHeadRoute`. The previous revision `0b076ca595d19951c536daf515c778b38cf6ba69` instead tested `opts.method !== 'HEAD'` as the third conjunct. The path and prefix prerequisites remain. Evidence: new `lib/route.js:250–274`, old `:250–273`.

Consequently, an explicit HEAD with a false generated marker is no longer excluded by the method comparison in that guard. This is a statement about the written condition, assuming earlier control reaches it; it does not guarantee successful registration for every possible input.

The local marker comes from `opts.isGeneratedHeadRoute = isFastify === true` after the options copy (`lib/route.js:206–213`). In the examined generated-HEAD path, `shouldExposeHead && isGetRoute && !isHeadRoute && !hasHEADHandler` guards a `prepareRoute.call` carrying `method: 'HEAD'` and `isFastify: true` (`:457–459`). `prepareRoute` later forwards `isFastify` to `route.call` (`:143–170`). These selected links explain the marker distinction; they do not exhaust every API caller.

The switch body and subsequent else branch are textually unchanged in this revision. The `slash` case passes `path`; `no-slash` passes an empty path. The `both`/default case first adds the empty path and adds the other path only under `ignoreTrailingSlash !== true && (ignoreDuplicateSlashes !== true || !prefix.endsWith('/'))`. If the outer switch guard is false, the subsequent branch may strip one leading slash when `path[0] === '/' && prefix.endsWith('/')`; otherwise it passes `path`. Evidence: new `lib/route.js:254–274`.

## FAQ

**Are all HEAD routes now handled identically?** No. The selected condition distinguishes the generated marker, while retaining path/prefix prerequisites and later branch conditions.

**Does a generated marker alone prove registration succeeds?** No. Earlier validation, later calls and runtime behavior are outside this static result.

**Were Fastify or its tests executed?** No. The existing TypeScript parser parsed the source in JavaScript mode and recorded lexical ownership. An owned Boolean abstraction explored the two guards; it does not establish reachability or application behavior.

This isolated candidate is ready for owner review only. It is not owner approved, training gold, an independent holdout score or an operational catalog update.
