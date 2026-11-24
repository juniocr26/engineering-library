# Totalist: source traversal and package boundaries

Isolated source-reviewed chapter candidate. Revision `4b071d3e54d466a4059de89006c752da782c8b02` (`3.0.1`); not published or approved for training. All source claims below refer to the preserved cut, not an installed package.

## Purpose and responsibilities

**C1** The pinned manifest names `totalist` version `3.0.1`; its `modes` maps `default` to `src/async.js` and `sync` to `src/sync.js`. [T1]

**C2** Both selected source modules declare the named export `totalist(dir, callback, pre='')`; the asynchronous declaration has the `async` modifier and the synchronous declaration does not. [T2] [T3]

**C3** Both bodies assign `dir = resolve('.', dir)`, obtain directory entries, form `abs` with `join`, and branch on `stats.isDirectory()` between recursion and a callback call. The callback expression receives the joined relative name, `abs`, and `stats`. [T2] [T3]

**C4** The asynchronous source wraps `stat` and `readdir` with `promisify`, uses `arr.map`, and supplies its results to `Promise.all`. Its inner callback returns either the recursive call or the user callback expression. [T2]

**C5** The synchronous source calls `readdirSync` and `statSync` inside an indexed loop. Its callback expression is a statement rather than a returned or awaited value; the selected function has no written return statement. [T3]

**C6** The source declarations type `Caller` as `(relPath: string, absPath: string, stats: Stats) => any`. The asynchronous return annotation is `Promise<void>` and the synchronous annotation is `void`; both declarations call the optional third argument `prefix`, while implementation source calls it `pre`. [T4] [T5]

**C7** The manifest exports `.` and `./sync`, each with `types`, `import`, and `require` targets. Those targets address generated distribution paths, not the two selected JavaScript source files directly. [T1]

**C8** The manifest declares `engines.node` as `>=6`, while the pinned README labels asynchronous mode `>= 8.x` and synchronous mode `>= 6.x`. This snapshot does not justify a single tested minimum Node version for both modes. [T1] [T6]

**C9** The selected bodies contain no written catch clause, explicit sort, traversal-depth limit, concurrency limiter, or explicit cycle registry. This is a bounded source inspection, not a guarantee about imported filesystem behavior or all possible runtime errors. [T2] [T3]

**C10** The preserved license is MIT. License presence alone does not approve a future training target, and this chapter remains excluded from training. [T7]

## Architecture and dependency table

| Layer | Written dependency or target | Evidence |
|---|---|---|
| async | `path`, `fs`, `util.promisify`, `Promise.all` | [T2] |
| sync | `path`, `fs`, `readdirSync`, `statSync` | [T3] |
| types | `Stats` from `fs`, `Caller`, `prefix` | [T4] [T5] |
| package | `.`, `./sync`, `types`, `import`, `require` | [T1] |

## Illustrative example and command

The example is syntax-checkable and unexecuted. Its import target is not authenticated by this study. No expected file list is invented.

```js
import { totalist } from 'totalist';
const relativePaths = [];
await totalist('src', (relativePath, absolutePath, stats) => {
  relativePaths.push(relativePath);
});
// Illustrative only: no particular result set or order is asserted.
```

```sh
node --check totalist-example.mjs
```

## FAQs

### Q1 — Can this snapshot certify the published package?

No. The complete pinned Git tree contains no `dist/` or `sync/` distribution files, and no registry tarball was authenticated or build executed. Manifest targets and source declarations are different evidence layers.

### Q2 — Does the callback prove that each entry is a regular file?

No. The written condition tests `stats.isDirectory()` and otherwise invokes the callback; it does not test `stats.isFile()`. Symlink behavior, access races and cycle safety were not exercised.

### Q3 — Does synchronous mode wait for a Promise returned by the callback?

The synchronous body contains no `await` and does not return or inspect the callback value. The declaration still accepts a `Caller` returning `any`; it supplies no static guarantee of asynchronous callback completion.

### Q4 — Which Node minimum should documentation state?

State the disagreement explicitly: manifest `>=6`, README asynchronous `>= 8.x`, README synchronous `>= 6.x`. No version compatibility execution was performed.

### Q5 — Are output order and bounded parallelism guaranteed?

No. The async source uses `arr.map` with `Promise.all`; neither selected body explicitly sorts or implements a concurrency limiter. This observation does not establish runtime scheduling or filesystem ordering.

### Q6 — Can unchanged parameter names justify a package-wide NO-OP?

No. Earlier source used a default export named `list`; this revision uses the named export `totalist`. Package metadata also adds an `exports` map. A signature-only observation cannot certify unchanged import examples or the whole chapter.

## Verification limits

No package installation, build, directory traversal, symlink probe, callback execution, imported dependency execution, runtime compatibility matrix, publication or owner review occurred. The example syntax check cannot certify import resolution or filesystem behavior.

## Source citations

[T1]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/package.json#L1 "0623891e622ac83bd53ef5a81987338da75697112e2386ffbd77676c1ef7e9df"

[T2]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/async.js#L1 "70a998ce6b3da13e242332e704d9b64ee88c23520ee260663d178206a57ae14d"

[T3]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/sync.js#L1 "0d911e865ba4c7e860a1ebb8e6fd7b25e5113967bea3e799bca690c48fdd41c0"

[T4]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/async.d.ts#L1 "9f78bd6e43202253f0af72af9978cda3399b5a1ae9cd28593976f42cf6a1f4ee"

[T5]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/src/sync.d.ts#L1 "4cdaa2f28b917cc3fb61454657fed974968a66557ef23c2858997565d3b9559c"

[T6]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/readme.md#L1 "fb37c2d537fe6d81bb653a447a192348f373577be88f2a1aa66696e751c6bf7d"

[T7]: ../new-public-sources-v1/lukeed--totalist/4b071d3e54d466a4059de89006c752da782c8b02/license#L1 "306fa513e39b23a6e8747520de761809d206b99800ef41907b530226574c59ae"
