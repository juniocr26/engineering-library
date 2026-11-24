# Zod core safe parsing: result branches and lazy errors

This chapter covers six selected source groups in `colinhacks/zod` at `2a343ed2a4ffbea73fb83862ee1e317662292481`: synchronous setup and the explicit Promise-guard throw, the result choice, the failure getter, the failure setter, the asynchronous counterpart, and the core factory bindings. It describes the written implementation in `packages/zod/src/v4/core/parse.ts`, not the entire Zod API or observed runtime behavior. The frozen repository has an MIT license; that does not supply owner approval for training or publication of this candidate.

## From a factory to a result

`_safeParse` takes `_Err` and returns an arrow accepting `schema`, `value` and `_ctx`. That arrow creates a context with `async: false`, overriding that property when it copies a supplied context. It calls `schema._zod.run({ value, issues: [] }, ctx)`. If the returned result satisfies the written `result instanceof Promise` guard, the function throws `new core.$ZodAsyncError()`. Thus “safe” does not mean that this synchronous implementation contains no throws. Evidence: `packages/zod/src/v4/core/parse.ts:71–76`.

If control reaches the following return, `result.issues.length` chooses `failure(_Err, result.issues, ctx)`. Otherwise the returned literal has `success: true` and `data: result.value`. These are the selected return branches, not a guarantee that every schema callback, property access or dependency completes normally. Evidence: `packages/zod/src/v4/core/parse.ts:78–79`.

The core `safeParse` constant calls `_safeParse(errors.$ZodRealError)`. Its asynchronous counterpart calls `_safeParseAsync(errors.$ZodRealError)`. These are bindings in this core module; this chapter does not establish every package import or instance-method path. Evidence: `packages/zod/src/v4/core/parse.ts:80,119`.

## A failure object has an accessor

`failure` declares an initially uninitialized local `error` and returns an object with `success: false`, an `error` getter and an `error` setter. In the getter, `if (!error)` guards construction through `new Err(...)`, with issues mapped through `util.finalizeIssue(iss, ctx, core.config())`. After that construction completes, the branch assigns `undefined as any` to both `issues` and `ctx`; the getter then returns `error`. Evidence: `packages/zod/src/v4/core/parse.ts:83–95`.

The setter first assigns its parameter `e` to the local `error`, then clears `issues` and `ctx`. A truthy replacement supplied before the getter runs therefore prevents that getter's construction branch from running on the later read, assuming the shown operations complete and no intervening reassignment. The actual guard is truthiness, not a separate “has been read” flag. The TypeScript parameter annotation is not a runtime validation guard. Evidence: `packages/zod/src/v4/core/parse.ts:96–101` and `:87–94`.

Do not turn this into an unconditional “the first read always constructs an error” contract. A setter can precede a read. Construction or finalization can also throw before the subsequent capture-clearing assignments. The selected code does not certify memory reclamation, performance measurements, arbitrary caller behavior or universal exception safety. The campaign did not reproduce the benchmark figures mentioned in the source comment.

## The asynchronous counterpart

`_safeParseAsync` returns an `async` arrow. It creates a context with `async: true`, calls the same written `schema._zod.run` shape, and awaits `result` if `result instanceof Promise`. It then uses the corresponding `result.issues.length` failure/success choice. Unlike the selected synchronous arrow, it does not contain that explicit Promise-guard throw. This does not prove that the returned Promise always fulfills or that dependencies cannot reject or throw. Evidence: `packages/zod/src/v4/core/parse.ts:111–117`.

## A small usage fragment

This illustrative fragment assumes that `safeParse`, `schema` and `input` have already been supplied. It shows result branching and an explicit read of the failure accessor; it is not a complete import or schema-construction example.

```typescript
const result = safeParse(schema, input);
if (result.success) {
  const data = result.data;
  void data;
} else {
  const error = result.error;
  void error;
}
```

Only TypeScript syntax is checked for this fragment. The core factory's selected returned arrow has the two required arguments shown here and an optional context according to its declared type. Module resolution, typechecking, dependencies and runtime behavior are not verified. Reading `result.error` is a distinct operation from merely testing `result.success`.

## Written tests, not passing observations

The frozen `packages/zod/src/v4/classic/tests/async-parsing.test.ts:8–19` contains a string test that awaits `safeParseAsync` for good and bad inputs, checks the two `success` values and conditionally inspects data or an error instance. The number test at `:23–34` writes analogous assertions. These are instance-method tests in a different module layer. They were not executed and do not independently prove the complete linkage to the selected core factories, the setter path or the synchronous Promise guard.

## FAQ

**Does safe parsing never throw?** That universal claim is unsupported. The selected synchronous arrow explicitly throws `core.$ZodAsyncError` under its Promise guard; other operations are not wrapped in a blanket exception handler here.

**Does checking failure necessarily construct the error?** The selected `failure` literal has a false success flag and a separate getter. Merely branching on that flag is not the written getter body. The getter constructs only while `!error` holds, and construction must complete before the shown clearing assignments.

**Can a replacement affect the later error read?** Yes, the written setter assigns the supplied value and clears its captures. A truthy replacement can make the getter return that value without constructing through `Err`; this is a source-level condition, not a guarantee about every untyped caller.

**Does the async variant guarantee success?** No. Its selected Promise guard awaits rather than executing the synchronous explicit throw, and its normal return still distinguishes issues from success. Rejections, schema contracts and arbitrary callback behavior are not certified by this static review.

## Evidence and limits

Exact source hashes, lexical owners, physical quotes and six registered fact groups are recorded in the isolated research evidence. The existing TypeScript parser reads source as text; it does not import or execute Zod. A separate reviewer reacquires public Git objects and queries their AST. Synthetic admission controls are development checks, not independent evaluation cases or a general semantic verifier. This chapter requires a completed review before source acceptance; owner approval, training gold, operational catalog integration and publication remain false.
