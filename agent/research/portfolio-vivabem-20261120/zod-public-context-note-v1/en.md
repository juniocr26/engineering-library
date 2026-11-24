# Zod: source entry points, instance methods and safe parsing

`colinhacks/zod` at `2a343ed2a4ffbea73fb83862ee1e317662292481`.

Isolated source-scoped follow-up candidate, not owner-approved, Gold or training data. The earlier core-only chapter remains unchanged. Eighteen public source, manifest, license and test files support this note; no Zod import, package installation, build, typecheck, parse or upstream test was executed.

## Export conditions are part of the boundary

The package root maps `@zod/source` to `./src/index.ts`, while `import` and `require` point to compiled JavaScript targets. The selected source entry reexports the classic external module, which reexports classic schemas, errors and parse wrappers, plus a core namespace. The source v4 entry also follows the classic exports. The two selected compiled root targets were absent from the pinned Git tree; this says nothing about an installed or published package. Resolver conditions and generated-build equivalence remain unverified. [Z01–Z07]

## Classic and core wrappers retain different bindings

Classic `safeParse` calls `core._safeParse(ZodRealError)`; its asynchronous counterpart supplies the same classic error binding to `core._safeParseAsync`. The core module exports wrappers built with `errors.$ZodRealError`. Both paths use the selected core factories, but their named constructor bindings must not be silently conflated. The classic instance member forwards its receiver, input and parameters to the classic wrapper. [Z08, Z11, Z21–Z23]

## One concrete construction path

The selected `string` function passes `ZodString` to `core._string`, whose body constructs the supplied class after helper calls. The selected constructor composes core string initialization, `_ZodString` and `ZodType` initialization. This establishes one written construction route toward the member table, not all schema types or success of every normalization helper. [Z10, Z12–Z15]

## Member reads can bind and mutate an instance

The selected constructor initializer installs trait members once for its selected prototype. `members` preserves getter descriptors but routes method values through `defineBound`. With an ordinary receiver, its getter binds the function and uses `own` to cache an own property; that descriptor is configurable and writable. A nullish receiver returns the raw method instead. This explains the selected detached-method design without promising success for frozen receivers, overridden descriptors or arbitrary objects. Reading a method is not necessarily a pure lookup. [Z16, Z19, Z20]

The `spa` getter reads `this?.safeParseAsync`; its setter can create an own value. It is a live alias in the selected getter path, not an immutable identity guarantee after arbitrary assignments or overrides. [Z11]

## Error objects and construction effects

The classic error initializer delegates to the core initializer and then sets the classic name. The real-error constructor supplies `Parent: Error`. The constructor helper has parent and trait branches in its custom `Symbol.hasInstance`; this is not an exact nominal-constructor identity test. The parent-error path calls a helper that can adjust stack-trace configuration while constructing an error. No actual prototype, stack or exception behavior was measured. [Z17, Z18, Z21, Z22]

Schema initialization can supply a default locale through global configuration. A global post-processor can run after initialization and deferred callbacks. These hooks and property installation prevent a blanket purity or unchanged-instance guarantee. The selected core synchronous parser still has its explicit Promise-guard throw, and failure still uses the lazy error getter/setter; public forwarding does not turn those contracts into universal no-throw behavior. [Z09, Z10, Z17, Z23]

## Written tests and reproduction

The selected tests assert detached parse-family use, spy replacement/restoration, the getter alias and lazy error construction. They are evidence of written expectations, not passing observations or certification of all receivers. [Z24–Z27]

From the public clone root, the following read-only command displays a selected source object. An equivalent Git acquisition was performed; this command does not import or run the module.

```sh
git -c core.fsmonitor=false show 2a343ed2a4ffbea73fb83862ee1e317662292481:packages/zod/src/v4/classic/parse.ts
```

## FAQ

### Does the root source export prove every installed import follows this path?

No. The source condition and compiled import/require targets differ. No build, installation or resolver execution was verified. [Z01–Z07]

### Does an instance safeParse call select the core module's exported error binding directly?

The selected member forwards to the classic wrapper, which supplies the classic error constructor to the core factory. Do not substitute the core module's separate exported binding. [Z08, Z11, Z21–Z23]

### Are detached methods guaranteed for every object?

No. The selected installation binds ordinary method reads, but descriptors, receiver shape, overrides and construction hooks matter. The tests were not run. [Z16, Z19, Z20, Z24]

### Can spa remain an immutable alias after assignment?

That is not established: its selected setter shadows the accessor with an own value. The ordinary getter is a different path. [Z11]

### Does safe parsing mean construction and lookup are side-effect-free?

No such guarantee follows. Initialization can configure defaults and call a post-processor, while method reads can cache own bound values. The synchronous core also retains an explicit throw branch. [Z09, Z17, Z20, Z23]

### Do the test assertions prove runtime correctness here?

No. They were inspected without execution. Source linkage, valid quotation hashes, type declarations, actual behavior and owner approval are separate evidence states. [Z24–Z27]

## Evidence and preservation

Z01–Z27 identify exact physical spans in the accompanying source-card index. They are manually selected spans, not complete native AST declarations or automatic semantic proof. The root MIT license and file notices remain preserved. No external repository, existing chapter, test suite or active catalog changed. This note remains restricted internal review material with no training or publication authorization.
