# Zod v4: synchronous and asynchronous parse boundaries

Isolated research candidate. Author source review only; separate verification and owner review pending. No publication or training approval.

colinhacks/zod @ `2a343ed2a4ffbea73fb83862ee1e317662292481`. This chapter covers the selected contract, not the full repository. Evidence: `source-freeze-v1.json`; criteria: `acceptance-protocol-v1.json`.

## Architecture and behavior

**Z01** — The synchronous _parse path runs schema._zod.run with async false, throws $ZodAsyncError for a Promise result and throws a constructed error when issues are present. [Z01: `packages/zod/src/v4/core/parse.ts:22-39`]

**Z02** — _parseAsync sets async true, awaits a Promise result, throws on issues and otherwise returns the resulting value. [Z02: `packages/zod/src/v4/core/parse.ts:48-63`]

**Z03** — _safeParse still throws $ZodAsyncError for a Promise result; safe does not establish that every failure becomes a returned object. [Z03: `packages/zod/src/v4/core/parse.ts:71-80`]

**Z04** — The failure object exposes success false. If no error has already been set, its getter constructs and caches error; the setter can supply a replacement, including before the first getter read. [Z04: `packages/zod/src/v4/core/parse.ts:83-103`]

**Z05** — _safeParseAsync awaits a Promise result and returns either failure(...) or a success true object with data. [Z05: `packages/zod/src/v4/core/parse.ts:111-119`]

**Z06** — The classic parse exports bind the core factories to ZodRealError, with explicit asynchronous return types for parseAsync and safeParseAsync. [Z06: `packages/zod/src/v4/classic/parse.ts:8-33`]

## Example

Synthetic usage fragment, not executed. Resolve dependencies in a separately authorized environment before running. No startup or installer command is authorized here.

```typescript
import * as z from "zod/v4";
const result = await z.string().safeParseAsync("sample");
if (result.success) console.log(result.data);
```

## Test evidence and limitations

`packages/zod/src/v4/classic/tests/async-parsing.test.ts` is preserved as written test evidence. No external suite, example, dependency installer or runtime was executed. Written assertions are not passing results. No benchmark, concurrency guarantee or release-wide API compatibility is established.

## FAQ

### Q001 — Can safeParse throw?

_safeParse still throws $ZodAsyncError for a Promise result; safe does not establish that every failure becomes a returned object. [Z03]

### Q002 — When is the failure error constructed?

The failure object exposes success false. If no error has already been set, its getter constructs and caches error; the setter can supply a replacement, including before the first getter read. [Z04]

### Q003 — What distinguishes the classic facade?

The classic parse exports bind the core factories to ZodRealError, with explicit asynchronous return types for parseAsync and safeParseAsync. [Z06]

## Maintenance and rights

This shallow clone has no local HEAD parent. A historical MODIFY decision is INCONCLUSIVE without a verified earlier source and matching documentation. Missing symbols in this selected scope do not authorize REMOVE. Existing project documentation remains unchanged.

MIT / LICENSE. Notices are preserved with the source snapshot. This artifact is evaluation-only, excluded from training and not owner-approved.
