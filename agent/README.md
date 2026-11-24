# Documentation-agent materials

## Exact model recovery — 2026-11-18

The approved existing deployment is `llama3.2:3b`, with runtime digest
`a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
`recovery/manifest.json` identifies every required Ollama blob, its size and
SHA-256, the original local manifest bytes, and the versioned agent files.
The lock also preserves the exact UTF-8 bytes of the six small configuration,
chat-template, stop-parameter, license and runtime-manifest blobs in ordinary
Git. Each embedded body is checked against its original size and checksum;
model weights are never embedded in this text manifest.
The local manifest hash differs from the runtime digest because it includes
the upstream manifest as an additional blob. Preserve both identities.
No locally fine-tuned adapter, dataset, or checkpoint is approved by this lock.

From the repository root, Python 3 with its standard library is sufficient for
offline verification. This host-side step handles the model bind mount before
Docker starts; it installs no Python dependencies. Use canonical absolute paths.
The verifier requires schema 1 and a complete, unique operational inventory,
with canonical paths and typed size/SHA-256 metadata. Unsupported or incomplete
locks are refused before model payload access or destination creation.

```sh
python3 agent/recovery/bootstrap.py knowledge
python3 agent/recovery/bootstrap.py verify
```

An independent local snapshot is prepared under the installation-private
`.local-backups/unattended-20261118/model-artifacts/` directory; its exact
versioned identity and local location are recorded in `recovery/manifest.json`.
This directory contains model artifacts only, without Ollama keys, and is
already excluded by the existing Git and Docker ignore rules.
It is not part of a clone and does not protect against loss of this computer.
Copying it elsewhere or publishing weights requires the owner's storage and
licensing approval. **REMOTE MODEL PERSISTENCE PENDING APPROVAL**.

For a fresh clone containing the reviewed recovery files, obtain that approved
snapshot through the separately approved storage mechanism. Before starting
Ollama, create the `ollama` parent directory if needed and restore into an absent
`ollama/models` directory:

```sh
python3 agent/recovery/bootstrap.py restore --source /APPROVED/SNAPSHOT --store /ABSOLUTE/CLONE/ollama/models
python3 agent/recovery/bootstrap.py verify
```

Restore verifies the source, copies into a new directory, verifies copied bytes,
and writes the model manifest last. An existing destination is refused even if
empty; no existing weights are replaced. On interruption, retain the incomplete
destination for inspection and retry into a different new destination. Do not
restore into an actively used store. Allow approximately 2.02 GB for each full
snapshot or restored copy, plus temporary workspace and Docker dependencies.

After initializing the existing Docker environment with the installation's
configuration and securely supplied secrets, run:

```sh
python3 agent/recovery/bootstrap.py runtime
```

This verifies local bytes and queries the existing backend-to-Ollama connection.
Both documentation workflows now check the selected model, active skill hashes,
and the full runtime digest before inference and again before accepting a
response. A mismatch fails closed; neither a different model nor a download is
used as a fallback. Other model selections require a reviewed replacement lock.
Missing response bodies, invalid envelopes and unexpected HTTP statuses also
terminate the project transport; redirects are not followed or retried across
other sections. The audit records a bodyless response without inventing bytes.
Invalid UTF-8 is also terminal with audit enabled; its exact bytes are recorded
as Base64 with the original checksum, without replacing invalid characters.
No-op generation and journal recovery that do not infer need no model request.
The first generation after the caller version change refreshes its fingerprint.
The approved model digest also enters that fingerprint and the generation
manifest; changing only artifact storage metadata does not invalidate content.

Git LFS is the preferred pending remote strategy, but is not installed on the
inspected host and no LFS attributes, hooks, transfers, uploads, or remote quotas
were configured. Ordinary Git must contain only the small lock and recovery
code. Review the provider's per-file limits, account quota, costs, access and
Llama license before enabling LFS. An immutable private artifact store with
checksummed retrieval is the alternative if LFS is unsuitable. A clone with
only LFS pointer files is not a recovered model.

`recovery/model-bundle.json` is the reviewed index for a local bundle with 14
parts of at most 256 MiB. It preserves the seven original blob identities,
including licenses, without depending on the provider's approximately 2 GB
single-file boundary. Parts remain in the installation-private directory above.
Only eight parts contain the large GGUF. If the six small parts are absent,
verification and restoration use the exact corresponding bytes sealed in the
Git lock. A small part that is present but incorrect is refused, never ignored
or overwritten. A future approved LFS checkout can therefore contain only the
eight weight parts; no remote retrieval has been configured or validated.
The bundle index and scripts are small ordinary Git files; no LFS pointers
have been staged or committed. To verify or recover this bundle:

```sh
python3 agent/recovery/bundle.py verify --bundle /APPROVED/PARTS-DIRECTORY
python3 agent/recovery/bundle.py restore --bundle /APPROVED/PARTS-DIRECTORY --store /ABSOLUTE/CLONE/ollama/models
```

The restore command trusts the versioned bundle index, verifies every part and
the complete reassembled blob hash, and refuses an existing destination.
It publishes the approved namespace entries only after all blobs pass. The lock
also preserves the exact relative `manifests-v2` link to the approved manifest
blob, alongside the legacy manifest. A regular-file-only copy misses that link.
Restoration requires filesystem support and permission to create symlinks;
Windows/WSL2 symlink privileges have not been validated. Unsupported creation
fails explicitly, with no copy fallback or overwrite. Embedded manifest metadata
is checked before creating the destination. For a new
local bundle, `bundle.py pack --bundle /NEW/PARTS-DIRECTORY --store /VERIFIED/MODEL-STORE`
requires a new directory and writes its candidate `bundle.json` there for
review; it does not replace the versioned index automatically. Enabling LFS
later requires a separately reviewed artifact path and LFS attributes. The
preferred final location remains under this agent subsystem. Before placing
weights there, approve an exclusion for that path in the existing root
`.dockerignore`: Git ignore rules alone do not exclude Docker build context.
The local preparation changed neither that protected file nor Docker services.

Revalidate the lock deliberately whenever operational files or the approved
model change. Exact artifact recovery does not guarantee identical generated
text across hardware or runtime versions. Local recovery validation does not
certify Windows/WSL2 or remote artifact availability.

Preserve Git checkout bytes when preparing another machine. For example,
`git clone --config core.autocrlf=false REPOSITORY_URL DIRECTORY` keeps the
checksummed text files from being converted to CRLF. After a future approved
LFS setup, its binary parts must retain `-text` attributes. A byte-changing
checkout is refused by the lock rather than silently normalized. This
prerequisite is not a claim of Windows runtime validation.

## Current caller contract — 2026-11-16

The authorized backend `make docs` caller loads evidence, authoring and review skills explicitly, calls Docker Ollama, and writes equivalent EN/PT-BR drafts and managed index links to both the library and narrowly writable analyzed-project docs destinations. Application source is read-only during normal generation. Default discovery visits direct siblings and excludes this library; additional collections are explicit installation configuration. Optional public URL retrieval/search uses bounded untrusted references and a separate local inference. No cloud fallback, automatic publication or model-weight training occurs. Mechanical validation does not prove factual/bilingual correctness. Current limitations and actual results belong in the dated run, not an implied approval.

Raw experiment requests, responses, checkpoints, recovery records and historical reports belong in private operational storage. The historical `runs/` tree was relocated with byte/mode verification and a separately verified archive into the existing Git-ignored recovery area during the extended 2026-11-16 campaign. Original records, failures, legal notices and historical hashes remain preserved; earlier committed copies remain in Git history. This relocation is not anonymization, deletion of evidence or authorization to publish.

The caller loads only the three active skill contexts below. Historical reports and reference answers are not model inputs. Curated examples and held-out evaluation materials require separate content/provenance review; neutral identities alone do not make a record safe to publish.

## Entry points

- [English instructions](instructions.en.md) and [Português brasileiro](instructions.pt-BR.md): equivalent authoring rules derived from the canonical [English](case-source://case-005/docs/en/training/documentation-standard.md) / [Portuguese](case-source://case-005/docs/pt-br/training/documentation-standard.md) standard. Preserve A/B/C/D classifications and scoped owner approvals; implementing a subset does not approve the whole standard.
- [Experiment procedure EN](experimental-session.en.md) / [PT-BR](experimental-session.pt-BR.md): explicit authorization, recovery, measured hypotheses and closure.
- [Source manifest](sources.json), [authoring examples](authoring.json) and historical evaluation materials in the private archive: provenance and draft-review records, not automatically approved answers. No implicit answer loading or gold promotion is permitted. Historical hashes describe historical inspections, not current freshness.
- [Skills provenance](skills/provenance.json): selected upstream practices, MIT attribution, explicit loader and current hashes. No upstream checkout is required.
- [Identity transformation](IDENTITY_NORMALIZATION.md) and historical inventory retained privately: normalized copies, legal exceptions, hashes, media and archive handling. Symbolic `case-source://` references are not executable installation configuration.
- Historical runs retain the interruption, resumption, failed candidates and recovery evidence in private storage. See the root-level `DOCUMENTATION_AGENT_EVALUATION_2026-11-16.md` for the current campaign status. No historical failure was retroactively marked successful.

## Operating boundaries

Use the current backend command/recovery guide in the actual library documentation. Source collections and real-name/case resolution stay in private transient installation configuration, never in portable artifacts. Discovery of both authorized collections is separate from the sibling-only default. The manifest now explicitly covers newly discovered evaluation repositories; classify source confidentiality separately from this installation's private status.

Read relevant source afresh, identify path/symbol/revision/hash and bound claims to observed evidence. A newer document is not automatically correct. Protect dotenv, credentials, owner data, clinical/personal data and financial payloads; synthetic local runtime checks are separate from authoring context. Exact quotations, typed JSON and successful builds do not certify prose or translation quality.

The owner decides scope and release. Keep one active rule set per responsibility, matching English/Portuguese guidance and explicit implementation limits. Preserve before-copies when consolidating obsolete instructions. Historical runs and reference answers are never an automatic model-context corpus. No inference changes weights, and no publication follows from retaining private records.


## Selected source locations — adaptive research 2026-11-18

The caller 1.9.20 validates each quotation at its exact selected source line
and retains that line in both languages. It does not search for the first
identical method body elsewhere in the file. This fixes citations that pointed
to another owner when multiple methods had identical text. Invalid, missing
or mismatching line metadata is refused before rendering. This check proves
source location consistency; it does not prove the explanation's semantics.

The [integration record](research/adaptive-20261118/citation-source-location.json)
pins the before/after evidence, current consumer and bounded regression result.
Raw drafts, rejected outputs and source snapshots remain in private research
storage. No training, automatic publication or remote preservation is implied.


## Explicit bounded source facts — adaptive research 2026-11-18

The opt-in `backend/lib/documentation/source_fact_command.rb` command reuses
the existing complete-unit collector, bilingual validator, ownership checks,
no-op fingerprint and interruption recovery. It emits deterministic source facts
instead of calling Ollama. Ordinary `make docs` model generation is unchanged.
From the existing backend, run `bundle exec ruby lib/documentation/source_fact_command.rb
--config /ABSOLUTE/RESEARCH/plan.json` as a single command with an explicit plan.
Use isolated source copies and an experimental library; set each project to
`lifecycle: temporary`. This is not automatic catalog publication.

The initial profile accepts only undecorated Python async declarations whose
body is a sole if/else, with one awaited call expression per branch. Every file
requires explicit `units`; unsupported syntax, decorated methods, computed
conditions/callees and nested call arguments are refused without model fallback.
The installed Python parser must understand the complete source module. This
is bounded syntax analysis, not general Python semantics or runtime execution.
Source expressions are AST-normalized; quoted source bytes and lines remain
verbatim. The command requires offline research and rejects authoring questions
and feedback rather than silently ignoring them.

Documents and generation records identify the source-analysis profile; each
fact includes its producer checksum, source citation and pending human review.
Logs say `inference: false`. A configured model identity in the shared recovery
metadata does not mean that model was invoked by this command. The strict
foreign-owner guard in model mode is preserved: only the exact source-derived
template with a matching AST derivation may cite its same-named awaited callee.

The [integration record](research/adaptive-20261118/source-fact-provenance.json)
distinguishes four accepted Core source workflows, eleven safe refusals, the
original failed eligibility projection, and regressions. Raw source snapshots,
original rejected drafts and complete experimental trees remain private. No
training examples, human approval, remote recovery or neural gains are implied.


## Go callback-factory source selection — adaptive research 2026-11-18

Explicit Go unit selection now preserves the whole outer definition when its
result is a supported function type, such as `func(next http.Handler)
http.Handler` or `func(*Manager)`. Returned callbacks with no result or a simple
named/pointer/slice result are supported. Anonymous struct/interface components,
complex callback result tuples, generic functions and receiver methods remain
outside this bounded extension. Bodyless declarations must not absorb a later
function's body. Exact spans were checked on ten functions across chi,
Prometheus and Temporal SDK Go; this is lexical layout support, not Go compiler
or runtime verification. See the [integration record](research/adaptive-20261118/go-callback-source-selection.json).


## Optional reuse of identical model requests - adaptive research 2026-11-18

A project or project section may explicitly set `reuse_selected_unit_facts: true`
to reuse an existing draft result when the complete prepared model request,
caller/provider/model identity and skill hashes are identical. This option is
disabled by default and requires offline, unassisted authoring with explicit
complete units covering every selected file. Source positions participate in
the key; moving the selected definition requires generation. Changes outside
the request can refresh full-file provenance without another inference.

The result and checksum remain in the generation manifest, with a separate
`source-model-result.json` per run. Cached results still pass the ordinary
validator and ownership/recovery checks. A corrupt cache is refused.
`SourceFactCommand` rejects this option because it does not generate model facts.
Project coordination forwards the option to its sections.

Reuse preserves draft text, including any factual errors. The real probe used
one model call followed by a metadata refresh and a no-op; its model text
invented a numeric interval and concurrency purpose and was rejected in both
languages. This proves request reuse, not correct documentation or training
quality. See the [integration record](research/adaptive-20261118/source-unit-result-reuse.json).


## Empty Go interface type boundaries - adaptive research 2026-11-18

The complete-definition selector now supports empty `interface{}` types in Go
results and returned callback types, including slices, maps and result tuples
containing that type. Only a private search copy is normalized; quoted source
bytes and line positions remain unchanged. This narrows the earlier anonymous
type limitation: interfaces with members and anonymous structs remain refused.
Receiver methods and generic declarations remain outside this extension.

Four newly available definitions across SQLx and a chi example have exact spans
through the actual Ruby consumer. A separate Temporal SDK tool fixture supplies
syntax transfer only. Sixteen frozen positive/refusal controls and the existing
regressions passed. This is bounded lexical selection, not Go compiler or
runtime validation. See the [integration record](research/adaptive-20261118/go-empty-interface-source-selection.json).


## Async source declaration syntax - adaptive research 2026-11-18

The source-only profile is now `python-async-dispatch-declaration-v2`. The same
bounded if/else awaited-call body is required. Each fact also records the
AST-normalized async declaration, including positional-only and keyword-only
markers, variadic parameters, defaults and annotations. These are recorded
syntax: defaults are not evaluated and annotations are not runtime validation.
The source quote remains verbatim. Unsafe inline text and declarations beyond
the bounded budget are refused, with no model fallback.

Four Core declarations became explicit without changing any prior branch IR.
The real workflow also accepted Starlette BackgroundTask dispatch and refused
the task-list loop. All seventeen pipeline cases matched expectations, alongside
thirteen parser controls and the existing regressions. Source-derived provenance
and pending human review remain explicit. See the [integration record](research/adaptive-20261118/async-declaration-source-facts.json).


## Optional JavaScript and TypeScript range preparation - adaptive research 2026-11-18

`agent/tools/javascript_ranges.cjs` uses an operator-selected installed TypeScript
parser to prepare explicit source ranges. In the existing frontend container:

```sh
docker compose exec -T frontend node /sources/engineering-library/agent/tools/javascript_ranges.cjs /app/frontend/node_modules/typescript < /ABSOLUTE/PRIVATE/packet.json > /ABSOLUTE/PRIVATE/ranges.json
```

The UTF-8 JSON packet has exactly `source` (original source string), `path`
(relative slash-separated source filename), and `selectors` (one to four names).
Top-level named functions, a single variable containing a function/block arrow,
and property assignments such as `Hooks.prototype.validate` are supported.
The output includes original line ranges, quote/source hashes and parser,
producer and Node identities. Inspected source is never required or executed.

Review the output and pass its `ranges` object to an isolated section plan using
the same exact source bytes. Large declarations split into contiguous chunks of
at most 1900 UTF-8 bytes; total context is limited to four cards. Ambiguous,
unsupported, unsafe or over-budget selections refuse without a model fallback.
Class/object/nested methods and overload collections are outside this profile.

This optional preparer uses the already installed frontend parser. It adds no
backend Node dependency or new service. The backend still consumes explicit
ranges with its existing caveat; AST boundaries do not prove types, helpers,
runtime behavior or model factual accuracy. It is not vector RAG. Run the tool's
twenty tests in the existing frontend with `node /sources/engineering-library/agent/test/javascript_ranges.test.cjs /app/frontend/node_modules/typescript`.
See the [integration record](research/adaptive-20261118/javascript-ast-range-preparation.json).


## Local recovery evidence for optional JavaScript tooling - 2026-11-18

A private Linux ARM64 archive now preserves the existing Node binary, TypeScript
package, linked libraries and available license notices. All 145 restored file
contents matched their recorded hashes. On the current compatible backend,
the restored Node and parser passed the same twenty tests through normal ELF
entry. The real AST CLI also reproduced exact ranges using the copied dynamic
loader and all seven restored library paths, without a global installation.

The explicit-loader test run retained an 18/20 failure: under manual ELF loader
entry, Node identifies that loader as `process.execPath`, so two tests that spawn
that path try to load JavaScript as ELF. Do not generalize the successful AST
CLI proof to arbitrary Node subprocess launchers. Windows, AMD64 and native
macOS recovery remain unverified. The archive is local/private, not remotely
persisted or automatically retrieved by bootstrap. See the [recovery record](research/adaptive-20261118/javascript-runtime-local-recovery.json).


## Private generation-attempt retention - adaptive research 2026-11-18

Normal documentation runs now keep reproducible evidence under each existing
`.docs-state/runs/<attempt>` directory, even when console `DOCS_AUDIT` is off:

- `generation-input.json` saves the accepted complete source snapshot, exact
  skill context, authoring inputs, model/settings and on-disk caller identity
  before inference.
- `generation-result.json` saves the provider result before validation.
- `generation-events.ndjson` appends transport/analysis events, including raw
  response text or invalid-UTF-8 base64 with the original checksum.

Each new run directory is created with mode `0700` and files with `0600`; POSIX modes
were verified on LinuxARM64. Inputs/results are write-once. A run-name collision
or input-persistence failure stops before another inference. Per-attempt state
is cleared on every exit. No-op and human-edit checks still precede a new run.
No raw payload is newly printed when console audit is disabled.

These private state directories already remain outside Git and Docker build
contexts. They can include original source and rejected output; preserve them
as private research artifacts and review before any redistribution. Retention
is not factual approval or a training dataset. No automatic deletion is added.
After interruption, validate JSON, checksums and journal state before resuming;
a partially written artifact must not be assumed complete. Direct `infer` calls
outside the normal run workflow still require their own explicit capture.
See the [integration record](research/adaptive-20261118/generation-attempt-preservation.json).


## Optional Go standard-parser source selection - adaptive research 2026-11-18

`backend/lib/documentation/go_ast_command.rb` is an explicit alternative to the
ordinary section command for Go projects. Use the same config shape with explicit
`files` and `units` for every file, without `ranges`. For example, from the backend:

```sh
bundle exec ruby lib/documentation/go_ast_command.rb --config /path/to/projects.json
```

Selectors support `Function`, `package.Function`, `Receiver.Method` and
`package.Receiver.Method`. Bare method names must be unambiguous. Complete original
line cards retain physical line numbers even with Go `//line` directives. Syntax
diagnostics, missing bodies, ambiguous aliases and adjacent same-line code refuse
the selected project before inference. The normal Command selector stays unchanged.

The optional launcher `agent/tools/go_source_ast.py` checks the local manifest,
Go source, license and native executable hashes before parsing source text. It
never compiles, imports or runs inspected source. Packaged static binaries cover
Darwin ARM64, Linux ARM64 and Linux AMD64. The last was tested through Docker
emulation on ARM64, not on a native AMD64 or Windows host. Unsupported platforms
or missing/tampered binaries fail without a lexical fallback. Python remains a
launcher dependency; Go is not needed at runtime.

This is syntax preparation, not type checking or runtime proof. The Go parser
accepts some forms broader than the language specification. Factory metadata
records literal signatures only; it does not establish helper semantics or
thread safety. Ordinary model output still requires factual and bilingual review.
No neural inference was needed to validate this integration. See the
[integration evidence](research/adaptive-20261118/go-standard-ast-optional-selection.json).

The compiler image and build cache are preserved in the private campaign archive;
source, BSD license, compiler identity, flags and executable hashes accompany the
packaged tool. No remote upload or Git staging was performed. Local manifest
checks provide consistency checks, not external signatures.


## Optional Go sole-return syntax facts - adaptive research 2026-11-18

`backend/lib/documentation/go_source_fact_command.rb` uses the same explicit Go
unit config as GoAstCommand, but produces bounded source-only facts without model
inference. Run it from the backend with `bundle exec ruby
lib/documentation/go_source_fact_command.rb --config /path/to/projects.json`
(on one command line). Offline mode is required; questions, feedback, public
references and model-fact reuse are rejected.

The profile records declaration/receiver syntax, ordered return expressions and
returned function-literal signatures. Returning a literal is distinguished from
executing its callback. Additional statements, unsupported expressions or oversized
paragraphs refuse the source-fact project without an inference fallback. A callback
body outside the profile is explicitly marked unanalyzed. This is not complete
behavioral documentation, type checking or runtime verification.

Quotes, physical lines, qualified symbols, full source hashes and producer hashes
remain attached to deterministic drafts. Human review and training approval are
still pending. No-op, source-change, owner-edit and transactional output protections
remain active. See [integration evidence](research/adaptive-20261118/go-sole-return-source-facts.json)
and [tool rebuild/recovery notes](tools/go-source-ast/README.md).

A separate [Clang ternary experiment](research/adaptive-20261118/clang-ternary-experimental.json)
verified three private source-only renderer cases with copied public headers. It
remains experimental: the backend imports precomputed records and does not rerun
Clang. No portable compiler/SDK bundle or production C++ profile is claimed.


Go AST cards now carry their AST-verified enclosing owner, so both the full
`package.Receiver.Method` and valid short `Receiver.Method` spellings pass the
existing ownership guard. Other receivers remain rejected, including methods
that exist elsewhere in the same file. This corrects a discovered false positive;
it does not approve generated factual claims. See the
[owner-validation correction](research/adaptive-20261118/go-ast-receiver-owner-validation.json).


GoAstCommand also accepts complete standalone Go type declarations in explicit
`units`, for example `DB`, `package.DB`, or a generic constraint such as `Ordered`.
Structs, interfaces, defined types and aliases retain their exact original lines
and an AST-derived `declaration_kind`. Grouped `type (...)` declarations remain
unsupported. Type context does not imply resolved imports or type relationships,
and the sole-return source-fact profile refuses type units. See the
[type-context integration record](research/adaptive-20261118/go-standalone-type-context.json).
The ordinary selector and model prompt/decoding defaults remain unchanged.


## Experimental project chapters for owner review - adaptive research 2026-11-18

Source-reviewed Codex correction drafts are available for
[SQLx EN](research/adaptive-20261118/chapters/sqlx/en.md),
[SQLx PT-BR](research/adaptive-20261118/chapters/sqlx/pt-br.md),
[Fastify EN](research/adaptive-20261118/chapters/fastify/en.md) and
[Fastify PT-BR](research/adaptive-20261118/chapters/fastify/pt-br.md).
They cover 13 sections and 35 paragraphs per language, with 212 matching inline code
terms, exact pinned source links and license/provenance records.

These chapters were authored by Codex after reviewing the original failed local
model drafts. The drafts and raw evidence remain preserved separately. This is
documentation correction, not autonomous Ollama improvement, neural training or
human-approved gold. Ordinary model context does not automatically load these
chapters. The public catalog is unchanged. See the
[chapter integration record](research/adaptive-20261118/source-reviewed-project-chapters.json).


A [private Go static-type probe](research/adaptive-20261118/go-static-type-probe-experimental.json)
verified eight SQLx/reflectx declarations and twenty controls, then generated eight
bilingual typed-fact pairs through a private renderer. Canonical types are labeled
separately from source spelling. Original module resolution was blocked by absent
driver metadata; the successful GOPATH probe is not a faithful go.mod build. No
program, upstream tests, model training or dependency download was performed. This
remains experimental and is not an ordinary agent loader or default profile.


## Optional JavaScript leading-guard source facts

`node agent/tools/javascript_leading_guard.cjs /absolute/path/to/typescript`
accepts one JSON packet on stdin with `source`, relative `path` and a one-item
`selectors` array. It requires an explicitly available Node/TypeScript runtime.
It reports the first body guard's written condition and return expression in
English and Portuguese, with exact source hashes and complete quotation.
Async/generator bodies, else branches, prefixes and unsupported statements are
refused. Lexical object paths, including dollar containers, do not establish
generated runtime ownership. Helpers, getters, parameter initialization and the
remaining body are unverified. This CLI is optional; the backend does not
automatically invoke it or require a new Node installation. See the
[guard evidence record](research/adaptive-20261118/javascript-leading-guard.json).

An explicit 8,192-token context trial retained exactly the same generated facts
as four 16,384-token requests. Ollama reported a smaller runner allocation, but
the responses retained their factual defects. This is an observed resource
tradeoff, not a default change or quality approval. See the
[context observation](research/adaptive-20261118/context-size-observation.json).
Private diagnostic datasets now preserve 79 complete bilingual pairs and two
truncated raw responses. No record is training-approved; no trainer or ordinary
model context consumes them. See the
[diagnostic dataset record](research/adaptive-20261118/diagnostic-dataset-supplements.json).

Both optional JavaScript preparers are now version 1.0.1. They reject literal
U+2028/U+2029 separators anywhere in source, including string literals, because
this bounded profile uses LF/CRLF physical citation lines. Version 1.0.0 could
associate a selected function with an adjacent function's quotation in a
constructed separator case. The original failures remain preserved. See the
[citation integrity fix](research/adaptive-20261118/javascript-physical-line-separators.json).


## Optional Go call/defer/return source facts

The explicit `backend/lib/documentation/go_deferred_fact_command.rb` entrypoint
accepts the existing project plan format with complete Go `files` and `units`.
It records a tightly bounded three-statement body: a zero-argument written
`Lock`/`RLock` call, a matching written deferred `Unlock`/`RUnlock`, then explicit
return expressions. It preserves expression order and nil polarity in EN/PT.
Matching method names do not prove mutex type, receiver identity in execution,
helper behavior or concurrency safety. A defer postpones invocation rather than
acting as an immediate second call; operand evaluation and runtime completion
remain outside this source-only evidence.

This profile is separate from the existing sole-return profile. It rejects
questions, feedback, web references and neural cache reuse, and keeps the normal
reader's path exclusions. Six real Prometheus/SDK Go workflows, 130 parser
controls per tested target and the full 217-test/1,316-assertion Ruby suite
passed. Windows and native AMD64 execution remain unverified. See the
[profile evidence](research/adaptive-20261118/go-call-defer-return-source-facts.json).


## Physical LF citation integrity across source preparers

Caller 1.9.32 aligns Python async facts and native body safety checks with the
reader's physical LF lines. Literal Unicode separators inside strings no longer
shift Python quotations or hide a native preprocessor branch from its refusal
check. LF and CRLF remain supported; bare CR is explicitly outside this profile.
The original failing quotes and workflow are preserved. All 17 frozen source
cases retain their prior complete IR/ENPT output or safe refusal; 219 Ruby tests
with 1,354 assertions and 29 native/Python range controls passed. Selected
generic async declarations remain outside the bounded fact profile. See the
[physical-line evidence](research/adaptive-20261118/physical-lf-source-provenance.json).


## Existing newer Python parser - private compatibility proof

The existing syntax producer was also run explicitly with the already installed
native Python 3.14.7 and cached Linux Python 3.14.10 image. Both produced identical
IR/ENPT or refusals across nine source cases. One Bravia declaration previously
blocked by the backend's older grammar became eligible; decorated methods remain
outside the profile. Three checksum-bound precomputed records passed the private
backend writer with no model or source-program execution. The normal backend
remains Python 3.11; no default parser fallback or dependency installation was
introduced. See the [compatibility evidence](research/adaptive-20261118/python314-parser-experimental.json).


The seven literal-contract-question comparisons yielded five factual rejections,
one inconclusive response and one truncation; the alternate question was not
adopted as a default. The 4,096-token resource trial kept the same incorrect
MinFunc facts while reporting a smaller runner allocation. A longer packet was
refused before inference by the unchanged conservative byte guard. Observations
are not peak-memory or controlled throughput benchmarks. See the
[question decision](research/adaptive-20261118/literal-contract-question-decision.json),
[resource observation](research/adaptive-20261118/context4096-resource-observation.json)
and [current diagnostic manifest](research/adaptive-20261118/diagnostic-dataset-progress-v7.json).


## Observed transport instruction echo

Caller 1.9.33 rejects a complete transport-schema imperative previously accepted
as source prose through a coincidental identifier substring. Replaying the four
stored entries now refuses the package before writing; legitimate technical
descriptions mentioning the same JSON keys still pass. This is a narrow format
guard, not factual or general instruction-echo validation. The full Ruby suite
passes 222 tests / 1,373 assertions. See the
[echo evidence](research/adaptive-20261118/schema-instruction-echo.json) and
[complete older-report review](research/adaptive-20261118/prior-report-review.json).


## Explicit model fact ceiling

`DOCS_FACT_LIMIT=5` explicitly allows up to five model facts in the normal writer.
The bounded setting accepts only `1` through `5`; the default remains `4`.
Prompt, schema, validation, fingerprint, exact-request reuse, retained inputs and
successful manifest bind the same ceiling. Project sections inherit the setting.
Changing it invalidates prior cache; an unchanged setting preserves no-op.
This enables retaining a fifth fact; it neither requires five facts nor approves
their accuracy. A real stored scalar response was refused at four and applied
unchanged at five, with zero new inference for that replay. The full suite passes
227 tests / 1,428 assertions. See the
[capacity evidence](research/adaptive-20261118/explicit-fact-limit.json).


A [source-reviewed Go chapter](research/adaptive-20261118/chapters/go-stdlib/en.md)
and its [Portuguese counterpart](research/adaptive-20261118/chapters/go-stdlib/pt-br.md)
correct observed comparison, zero-value, binary-search and minimum-scan errors.
The cached compiler image identifies the preserved source; no Git revision is
invented. Exact quotations and the original license accompany the chapter.
These are Codex-authored correction drafts pending human approval, without
automatic model-context, catalog or trainer integration. See the
[chapter evidence](research/adaptive-20261118/go-stdlib-source-reviewed-chapter.json).


## Go if-return and fallthrough syntax facts

`bundle exec ruby lib/documentation/go_if_return_fact_command.rb --config PLAN`
selects explicit Go units with exactly an initializer-free if/sole-return and a
following return. It preserves the written condition, both ordered expression
lists, signature and receiver. It does not infer a helper call's number of
returned values, types, side effects or runtime completion. Initializers, else
branches and extra statements are refused. The ordinary model path is unchanged.
Six real Chi/SQLx/SDK/Prometheus workflows passed, including same-named type and
callee references bound exclusively to immutable source syntax. Arbitrary model
prose receives no exception. The full suite passes 234 tests / 1,494 assertions;
158 parser controls passed per tested target, with AMD64 emulated. See the
[profile evidence](research/adaptive-20261118/go-if-return-source-facts.json).

The six raw maxItems-only trials preserved a fifth scalar helper while keeping
the first four fact objects identical; the two-helper and Ruff outputs retained
their defects. Six further actual normal workflows emitted one fact each,
without a fifth-helper gain; none received whole-response approval. Optional
capacity works, but default four remains unchanged. As of this review, private
diagnostics preserve 91 complete bilingual pairs plus two truncated responses;
zero are training-approved. See the
[generation decision](research/adaptive-20261118/fact-ceiling-generation-decision.json).


The guard profile also passed 14 actual incremental workflows on an owned SQLx
copy: physical no-op, irrelevant-comment metadata refresh, negation/restoration,
CRLF simulation, rename with same-named helper preservation, missing-unit refusal
and protection of a simulated human edit. Original bytes were restored and the
human fixture retained. This is not native Windows execution.

A separate private candidate dataset now preserves 17 source-syntax pairs from
three deterministic profiles, with 16 complete source files, original licenses
and the Prometheus NOTICE supplement. Exact current targets match previously
reviewed delivery paragraphs; both languages and physical quotations pass the
integrity reader. All candidates remain unapproved for training; two broad
family components do not establish a diversified holdout. They are separate
from neural diagnostics and are not loaded by any trainer or ordinary model
context. See the [incremental and candidate evidence](research/adaptive-20261118/go-guard-incremental-and-source-candidates.json).


Three new normal Go AST neural baselines on the same guard contracts all failed
whole-response review. One invents errors where the visible continuation returns
`nil, nil`; another attributes parser-preparation metadata to the application
method. The source-only profile preserves the exact written branches while
keeping helper/runtime behavior unknown. This is a bounded source-syntax gain,
not learned model weights or complete behavioral documentation. The audited
ledger now contains 97 real completed calls: 96 documentation responses (94
complete pairs and two truncations) plus one restored-runtime probe. Private
source-syntax candidates remain separate. See the
[comparison and current diagnostics](research/adaptive-20261118/go-guard-neural-baselines-and-diagnostics-v10.json).


The frozen guard profile was then tested on 20 additional contracts: 15 yielded
exact reviewed bilingual syntax facts and five refused. Initial predictions
matched 19/20: pointer dereference uses an unsupported StarExpr, so that safe
refusal remains rather than extending the profile for the score. The expression
subset constrains outer AST kinds and formatted text; it does not recursively
exclude every nested literal or establish side effects. Source-only output keeps
those limits explicit. The same 234-test / 1,494-assertion suite also passed from
the normal backend layout using the existing read-only /agent mount. See the
[transfer and layout evidence](research/adaptive-20261118/go-guard-transfer-and-runtime-layout.json).


The final source/response integrity pass expands all 96 documentary request
packets and verifies all 188 diagnostic language rows against their original
HTTP responses and linked source/review/raw hashes across ten append-only data
versions. The additional restored-runtime probe makes 97 real completed calls.
There are 146 unique preserved public project source files and 11,130 distinct
automated scan paths; those scans are not manual whole-repository review.
Per-repository inventories and the exact measurement coverage are linked in the
[integrity audit](research/adaptive-20261118/source-and-diagnostic-integrity-audit.json).
No model answer was repaired or promoted to training gold during that audit.


## Latest independently exercised recovery cut

The 09:01:21 UTC capsule contains caller 1.9.35 and Go AST 1.4.0. A fresh
local clone overlaid only from independent extraction passed 234 Ruby tests /
1,494 assertions, 28 native Go launcher controls and 29 native/Python preparer
controls. Four real source profiles ran with code and inputs from that recovery.
The extracted optional JS runtime verified all 145 files and passed 56 full
tests plus two CLI cases using recovered code. Rebuilding the Go inspector from
extracted source with a fresh cache reproduced all three packaged binaries byte
for byte. Original model metadata/store remained unchanged; all five services
were healthy with start times preceding this campaign.

This is local recovery with explicit existing-runtime dependencies. Model parts
remain separate; no remote/LFS or Windows recovery was demonstrated. This note
and the final report postdate the immutable cut and need the final artifact
capsule. See the [recovery evidence](research/adaptive-20261118/caller35-independent-recovery.json).


The current learning-consumer audit distinguishes dated research records from
actual method/CLI consumption. Eighteen current method locations match the
independently exercised clone. It also corrects a metadata typo append-only:
`source-unit-result-reuse.json` called the consumer `Command.process_project`,
while the actual method is `Command.process`; no such process_project method
exists. Older dataset/tool counts remain dated snapshots rather than silently
rewritten current claims. No research JSON or candidate data is automatically
loaded by a trainer or ordinary model context. See the
[consumer reconciliation](research/adaptive-20261118/learning-consumer-reconciliation.json).

## Continuation on 2026-11-19 — caller 1.9.36

Explicitly selected source files must be valid UTF-8 text without NUL. Previously,
an invalid selected helper could be silently omitted while other files still
produced replacement documentation. The ordinary `Command#evidence` path now
refuses that selection before inference or output changes. The existing section
workflow already refused invalid text. Two regressions reproduced the defect;
the corrected full offline suite passed 236 tests / 1,508 assertions. See the
[source-completeness evidence](research/continuation-20261119/source-completeness.json).

The recovery inventory's absent historical root report is preserved with its
exact verified bytes under `research/continuation-20261119/history/`; the manifest
references that archival location. Original report bytes and their historical
repository-root-relative links are retained, not rewritten as current findings.
Knowledge verification and original-store verification passed. An independent
filesystem snapshot and separately restored model store are preserved privately;
their executed checks remain distinct from remote recovery.

The [architecture investigation](research/continuation-20261119/agentic-architecture.md)
maps the actual application-directed loop, optional syntax profiles and fixed
skill-context loading. It does not establish MCP or Agent Plugins conformance.
The [bounded helper-retrieval experiment](research/continuation-20261119/helper-retrieval-proposal.json)
is a proposal requiring a separate implementation decision. No new harness,
MCP server, plugin package or production tool routing is installed by that work.

The existing explicit source-selection comparison for Prometheus did not produce
a complete factual improvement: supplying `Builder.Del` allowed structural writer
acceptance, but its explanation and a previously mentioned return were omitted.
The [decision](research/continuation-20261119/helper-set-decision.json) preserves
that negative result. Its [EN/PT source-reviewed correction](research/continuation-20261119/chapters/prometheus-builder/en.md)
is authored by Codex, pending human approval; it is not neural learning.

Git LFS 3.8.1 is available as private local tooling with a verified release-asset
checksum and synthetic local clean/smudge roundtrip. Repository/global filters,
hooks, staging and history are unchanged; nothing was uploaded. See the
[local-only receipt](research/continuation-20261119/git-lfs-local-validation.json).
The [module study](research/continuation-20261119/go-module-resolution-study.json)
also records why an actual nested `go.mod` declaration, rather than a Git remote
or repository slug, must govern a future module-aware resolver. No semantic
resolver or automatic training-data promotion is implied by these records.

### Continuation follow-up — caller 1.9.38 / Go AST 1.5.0

The optional Go AST path now records an exact same-callback defer/direct-call
layout and refuses the observed positive EN/PT order error. It leaves unsupported
shapes alone and makes no general semantic-analysis claim. A keyword-only attempt
was rejected on a valid nested-function counterexample. A further regression
preserves faithful quotation of misleading comments, as well as correct and
negated descriptions. The default lexical command does not pretend to have this
AST proof. The new caller version invalidates older no-op fingerprints.

The full suite passed 240 Ruby tests / 1,518 assertions. The real earlier response
was replayed without a new model call: it was refused while all eight owned output
files retained their bytes and mtimes. Parser/launcher tests passed natively on
macOS ARM64 and Linux ARM64; AMD64 coverage was emulated, not native or Windows.
Model weights were not trained or changed.

An independent restored store also completed an actual bounded inference with
the approved digest. Only the owned temporary loopback process was stopped; the
original service remained healthy. See the
[local recovery receipt](research/continuation-20261119/independent-recovery.json).
The [tool notes](tools/go-source-ast/README.md) explain the exact source-path
requirement discovered during compiler recovery. Historical build-ID divergence,
counterexamples and replay harness failures remain preserved privately.


### Optional Python awaited-return record — profile v3

The existing source-only Python command additionally accepts one narrow module-level
async shape: a local parameter is reassigned from a call with that parameter,
`*args` and `**kwargs`, followed by a sole `return await` call using the reassigned
parameter. It records the exact expressions and says the result is returned if the
awaited expression completes normally. It does not infer imported helper bindings,
thread scheduling or successful execution. Methods, extra statements, changed
argument shapes and computed callees are refused by this new shape. The prior
if/else dispatch text remains byte-identical in EN/PT.

The profile is `python-async-dispatch-and-return-v3`; producer and consumer hashes
remain part of evidence identity. The real frozen Starlette wrapper generated
source-only drafts and then a no-op without model transport. The full suite passed
243 Ruby tests / 1,573 assertions and 36 Python tests; seven new Python controls
also passed on the native host. The
[integration receipt](research/continuation-20261119/python-awaited-return-integration.json)
keeps baseline refusal, limited claims and a corrected negative-test fixture.
This is a deterministic optional-profile improvement, not neural training or a
new tool-selection loop.


### Complete selected-unit byte bound — caller 1.9.39

The common source-unit collector now applies the shared 6,144-byte quote limit
to UTF-8 bytes, matching the optional Go AST and Python fact producers. A shorter
character count previously allowed an oversized multibyte unit to reach inference.
Two regressions reproduced the gap. Exact-boundary ASCII and multibyte units in
Python and the native Go layout profile pass; one-byte-over units refuse. An
oversized changed selection preserves prior output bytes and mtimes before any
further inference. The full Ruby suite passed 245 tests / 1,601 assertions.
The [receipt](research/continuation-20261119/complete-unit-byte-limit.json) preserves
initial test-fixture corrections and the restricted scope.


### Ordered Go guards — explicit source-fact profile v2

The existing Go if-return CLI additionally records two or three initializer-free
if-return guards and a final explicit return. Each later test is conditional on
preceding tests completing false. Written names and helper expressions remain
syntax, without binding or runtime proof. The prior one-guard paragraph stays
identical; profile and producer hashes change the evidence identity. Ordinary
`make docs` routing is unchanged.

Real quality and SQLx scannability contracts pass the owned writer followed by
no-op, without model transport. Guard reordering invalidates analysis, unsupported
changes preserve all eight owned outputs, and foreign same-name callee mutations
remain refused. Producer 1.6.1 fixes a reproduced logical-versus-physical line
defect in its first candidate. Checks passed 249 Ruby tests / 1,652 assertions and
34 producer controls per tested target, with AMD64 emulated. All three binaries
were independently reproduced byte for byte. See the
[receipt](research/continuation-20261119/go-ordered-guard-chain-integration.json).
No neural training, autonomous retrieval or new Harness/MCP/plugin is involved.


### Standalone JavaScript ordered-guard packet — producer 1.1.0

The existing leading-guard CLI adds an optional `ordered_guard_chain` packet for
exact synchronous bodies with two or three if-return guards and a final return.
The prior leading-guard IR and English/Portuguese paragraphs stay unchanged.
Unsupported full chains retain that earlier partial-analysis boundary. The new
packet preserves ordered conditions, written return expressions, physical lines
and hashes without binding, helper/getter, parameter or runtime proof.

Three real cases from Fastify and Go Image Optimizer passed the actual CLI; the
request/reply pair is one family. All 37 permanent controls and six private
prototype controls passed. An independently restored archived Node/TypeScript
runtime verified 145 files and produced identical CLI results with both normal
and bundled-loader entries. The first Python extraction-API incompatibility and
its explicit hash-checked fallback are preserved. See the
[receipt](research/continuation-20261119/javascript-ordered-guard-packet.json).

This is a standalone producer improvement. The ordinary Ruby documentation path
does not automatically consume the new child packet. No new production routing,
MCP/server/plugin, UI change or neural training is included.


### Project-wide source consistency — workflow 1.0.7

The project coordinator retains each selected path's first collected SHA-256,
refuses conflicting later reads before replacing staged source, and rechecks
all collected paths before final assembly. This catches changes to an earlier
section's source while a later section is running. Prior assembled EN/PT output
and its manifest are preserved on refusal; isolated section drafts and audits
remain available. This is a final content recheck, not an atomic filesystem
snapshot or source lock.

The header and manifest now distinguish observed Git HEAD from collected
working-file bytes. Committed-tree equivalence is explicitly unchecked; dirty
working files are not newly prohibited. Three regressions reproduced the earlier
acceptance/provenance gap. The full Ruby suite passed 252 tests / 1,679 assertions,
including 30 project tests / 208 assertions. See the
[receipt](research/continuation-20261119/project-source-consistency.json).
No model or external source program was executed by these regressions.


### Optional Python guarded iteration — profile v4

The existing explicit Python source-fact workflow additionally records one narrow
module-level async-generator shape: a distinct local initialized by a named call,
`while True`, a sole `yield await` call inside a try, and one named exception
handler containing only `break`. Altered handlers, extra work, loop/try else,
finally, computed callees and changed argument shapes are refused. The generated
paragraph preserves the expressions and separates a yielded result from a final
return. Exception matching, imported helper behavior and thread scheduling remain
unverified. The actual inspected application is never imported or executed.

The current profile is `python-async-dispatch-return-and-iteration-v4`. Both earlier
shapes retain byte-identical EN/PT paragraphs. Source/profile hashes invalidate
prior identities. The frozen Starlette iteration case changed from unsupported
refusal to a deterministic draft and then no-op, preserving every output byte and
mtime on rerun. The supported evidence is one real repository family plus owned
renamed/adversarial controls; independent real-repository transfer is not claimed.
Checks passed 254 Ruby tests / 1,704 assertions and 46 Python tests on the host and
Linux runtime. See the
[receipt](research/continuation-20261119/python-guarded-iteration-integration.json).
The ordinary model path and production tool routing remain unchanged.

### Reviewed experiments and consumer limits

The actual twelve-pass local-agent self-documentation run produced forty bilingual
fact pairs. Nine sections passed the writer, three were refused, and no whole
response was approved after factual review. A separate corrected chapter records
source selection, fixed skill consumption, model identity, transport, ownership,
reuse and source consistency. See the
[review](research/continuation-20261119/agent-self-documentation-review.json) and
[corrected chapter](research/continuation-20261119/chapters/documentation-agent-contracts/en.md).

A private Ruby lexical-owner metadata experiment passed parser controls but was
rejected after a critical factual regression on installed Rails source. It did
not change live source-card metadata. See the
[decision](research/continuation-20261119/ruby-lexical-owner-experiment.json).
Preserved research, diagnostic datasets and corrected chapters are not loaded
automatically by `skill_context` or a neural trainer. They remain review material,
not approved gold or evidence of model-weight improvement.

The [module-boundary study](research/continuation-20261119/go-module-boundaries.json)
parsed 34 frozen module declarations and one workspace across five repositories,
without building applications or fetching dependencies. Its nested modules,
local replacements and remote/declaration differences are documented acceptance
criteria for future resolution work. No module-aware resolver was installed.

### Explicit selected-evidence coverage — caller 1.9.40 / project 1.0.8

A project specification, or an individual project-plan section, may set
`"require_selected_evidence_coverage": true`. The default is false. When enabled,
every selected evidence ID must appear in at least one fact, and the number of
cards must fit `DOCS_FACT_LIMIT` before inference. Repeated IDs cannot cover a
missing card. The request asks for all IDs and raises the schema's minimum fact
count; the caller still enforces actual ID coverage after its existing checks.
An impossible budget or invalid non-Boolean value is refused.

The policy participates in fingerprints, exact-result reuse identity, generation
settings and manifests. Changing it cannot silently keep a partial no-op or reuse
a partial cached answer. On refusal, prior owned outputs and their manifest stay
unchanged. Default and explicit-false requests remained byte-identical to the
previous caller across three actual source cases. The version update invalidates
older fingerprints once; it does not change the default coverage policy.

Two historical incomplete responses from independent development repositories
were replayed through the real writer with zero new model calls; explicit
coverage refused them while preserving all output/manifest bytes and mtimes.
A known wrong response covering every ID still passed, demonstrating that this
policy is a coverage check, not a semantic or bilingual correctness guarantee.
The full suite passed 262 Ruby tests / 1,787 assertions. See the
[receipt](research/continuation-20261119/selected-evidence-coverage-integration.json).
No automatic helper discovery, new tool dispatch or neural training is involved.

### Current source-candidate reconciliation

The historical 17 source-syntax pairs were regenerated with current verified
producers on native Darwin ARM64 / Python 3.14 and Linux ARM64 / Python 3.11.
Every prior EN/PT paragraph, quotation and physical line matched exactly. Four
new contracts match the already verified writer deliveries: ordered Go quality
and scannability guards, Python awaited return and guarded iteration. The new
private append-only cut therefore has 21 unique pairs / 42 language rows, with
19 source files and complete notices. Runtime variants and prior versions are
not additional independent examples. See the
[reconciliation](research/continuation-20261119/source-syntax-candidate-reconciliation.json).

This chain is separate from 142 neural diagnostic pairs / 284 language rows and
14 Codex-authored corrected chapter pairs / 28 language rows. Its two broad
connected components are development-exposed. No chain is automatically loaded
by the ordinary prompt context or a trainer, and none contains approved gold.

The [current recovery receipt](research/continuation-20261119/current-code-recovery.json)
records the independent 1.9.40 / 1.0.8 source cut and runtime-entry limitation.
A private [name-binding study](research/continuation-20261119/go-predeclared-binding-study.json)
retains a safe refusal caused by an ignored generator with a different package
clause. No predeclared-name proof or production resolver was promoted from it.

### Additional C/C++ and Rust contract corrections

Four actual wave-two baselines now have paired source-reviewed corrections:
OpenCV trailing-shape/channel checks, Redis TTL reply units and sentinels,
DuckDB Boolean factory versus constructor, and Ruff's Python-version result.
The exact source revisions match the frozen Git objects. The paired chapters
have identical technical code-span sequences and retained source notices.
The corrected chapter chain now has 18 pairs / 36 language rows, separate from
142 diagnostic pairs and 21 unique source-syntax pairs. All remain pending
owner review, with zero approved training gold and no automatic consumer.
See [the chapter receipt](research/continuation-20261119/four-language-contract-chapters.json).
No additional model calls, framework installation or production route was used.

### Live coverage policy and unified lineage audit

Two bounded actual inference arms cited all previously selected evidence IDs:
own model identity moved from 1/3 to 3/3; image-dimension helpers from 1/2 to
2/2. Source review still rejects the own response's invented `installed` method
and marks the image contract incomplete because exact error distinctions are
missing. Coverage is not factual truth. See the
[live comparison](research/continuation-20261119/selected-evidence-coverage-live.json).
The current audit has 52 actual requests: 50 documentary development responses
and two independent model-restoration smokes; replays are excluded.

The private provenance index checks 23 immutable manifests and 414 referenced
files, then resolves seven older repository labels from exact source hashes
or the original synthetic-fixture protocol. It ties 144 diagnostic pairs,
18 corrected chapter pairs and 21 source-syntax pairs into 12 conservative
development components, with zero approved training rows or held-out components.
See [the lineage audit](research/continuation-20261119/unified-candidate-lineage-v2.json).

A [private same-module directory study](research/continuation-20261119/same-module-index-study.json)
verifies five declared same-module imports, refuses two cross-module imports,
and retains the GIO module-root-without-Go-files refusal. It is not a production
resolver and does not establish package names, build constraints or name bindings.

### Post-restart evidence and current candidate totals

An accidental owner power-off restarted the existing containers at 19:01:54 UTC.
The preserved chi response survived; an old SQLx request had no recorded response.
A separately authorized replacement used an identical frozen request and retained
its actual response and writer refusal. The audit now distinguishes 54 completed
responses (52 documentary development cases and two recovery smokes) from one
old request attempt with unknown server outcome. No unknown tokens or successful
inference were invented. See [the incident diagnosis](research/continuation-20261119/power-restart-analysis.md)
and [the current inference audit](research/continuation-20261119/inference-call-audit-after-restart.json).

Current private chains contain 146 diagnostic pairs / 292 language rows,
22 Codex-authored corrected chapter pairs / 44 rows, and 21 unique source-syntax
pairs / 42 rows. The [current lineage audit](research/continuation-20261119/unified-candidate-lineage-v4.json)
checks 26 immutable manifests and 436 referenced files, with 12 conservative
DEVELOPMENT components and zero certified holdout components or approved gold.
None of these research chains is automatically loaded into inference or a trainer.

[Independent chapter checks](research/continuation-20261119/chapter-citation-integrity.json)
verify all 44 current language files, 95 source quotations and 29 frozen file
identities. A [separate Git identity check](research/continuation-20261119/chapter-source-git-identity.json)
verifies 23 external source files at their pinned commits; owner working-code
snapshots and installed Rails gem source retain their distinct provenance roles.
These integrity checks do not confer owner approval or factual truth by themselves.

The [response matrix](research/continuation-20261119/response-outcome-matrix-v2.json)
links every one of the 52 actual documentary responses to review evidence:
41 passed the writer, 11 were refused, 43 cited all selected IDs, nine omitted
IDs, and zero whole responses were source-approved. These deliberately difficult
development cases are not a random sample or a global accuracy estimate.

A [zero-network cross-file cache study](research/continuation-20261119/cross-file-helper-cache-study.json)
confirms that a changed explicitly selected helper invalidates exact-result reuse,
while an unselected helper can refresh full-file metadata without changing the
selected-context explanation. A deliberate refusal preserved all eight prior
outputs and the manifest. This is not automatic dependency discovery.

A [read-only Git metadata archive](research/continuation-20261119/git-metadata-recovery.json)
retains all 731 local metadata/object files, with restored HEAD and full object
verification, while the original index and every captured metadata hash remain
unchanged. It supplements working-file/model capsules; no Git history was rewritten.

### Latest continuation cut: recovered parts and bounded Redis helper study

This dated supplement supersedes earlier current-count paragraphs while retaining
those observations. The [latest response audit](research/continuation-20261119/inference-call-audit-complete-helper.json)
contains 56 complete responses: 54 documentary development responses and two
independent restored-model smokes. One older power-interrupted attempt still has
unknown server outcome. A refused explicit-range helper preflight is not a model
request. No response or token count was invented for either case.

Current candidate chains contain 148 diagnostic pairs / 296 language rows,
24 corrected chapter pairs / 48 files, and 21 unique source-syntax pairs / 42 rows.
The [latest lineage cut](research/continuation-20261119/unified-candidate-lineage-v6.json)
checks 29 immutable manifests and 454 unique reference files, plus the recorded
repository-resolution comparisons. Its 193 category pairs stay within twelve
DEVELOPMENT components, with no certified holdout or approved training gold.
Two additional chapters reused exact historical caller1.9.22 baselines; those
historical requests were not recounted in this continuation's 56 responses.

The [current citation checks](research/continuation-20261119/chapter-citation-integrity-v2.json)
verify 97 quotations and technical-span parity in all 48 chapter language files.
The [current outcome matrix](research/continuation-20261119/response-outcome-matrix-v4.json)
records 42 writer acceptances, twelve refusals, 45 answers citing all selected IDs,
nine with partial ID coverage, and zero wholly approved documentary answers.
These are selected difficult development cases, not a global accuracy estimate.

The [Redis range study](research/continuation-20261119/redis-active-expiry-helper-study.json)
retains a critical guard/return/counter-name failure and a safe preflight refusal:
the complete helper has 2,357 bytes, above the existing 1,900-byte explicit-range
limit. A [distinct existing complete-unit selection](research/continuation-20261119/redis-complete-helper-unit-study.json)
retained all helper bytes under its already established 6,144-byte unit limit.
That response cited all three IDs but still introduced ownership, propagation and
branch errors, and the writer refused it. No limits, production routing or
extractors were changed. The comparison is exploratory because selection metadata
differs; neither source retrieval nor full ID coverage proves factual correctness.

[Post-restart framework probes](research/continuation-20261119/post-restart-framework-readiness.json)
found the eight training frameworks unavailable on both runtimes without imports
or installations. The [remaining-queue preflight](research/continuation-20261119/remaining-queue-preflight-v2.json)
separates 53 pending rows into 24 contract groups and does not promote them to READY.
The [eight-part recovery](research/continuation-20261119/chunk-recovery-after-restart.json)
independently reconstructs the original weight hash after restart, preserving all
original parts and the original store. No additional restoration inference or
remote upload was needed.

## Documentation intelligence campaign — 2026-11-19, in progress

This supplement describes the new local research cut. Earlier dated counts and
failures above remain historical observations. Publication, staging, commits and
model training are not authorized by these artifacts.

The [chapter review](research/documentation-intelligence-20261119/chapter-review-integrity-v3.json)
checks all 24 historical EN/PT chapter pairs against preserved sources:
95 original files remain unchanged, 131 quotations are byte-checked and 72 FAQ
pairs were added to review candidates. A new [synthetic adapter chapter](research/documentation-intelligence-20261119/owned-adapter/en.md)
has an equivalent [Portuguese version](research/documentation-intelligence-20261119/owned-adapter/pt-br.md),
five FAQs, a fake-client example and eight passing fixture tests. These are
Codex-authored source reviews pending owner approval, not approved training gold.

New tools remain explicit opt-in research APIs. The lifecycle planner 0.3.3
distinguishes five actions within its closed source/claim profiles. Separate
candidate/workspace tools preserve human content and prepare isolated outputs.
The restricted [FAQ experiment](research/documentation-intelligence-20261119/faq-maintenance-evaluation.json)
uses explicit question identity and integer-return claims; it does not perform
general paraphrase detection. The optional [retrieval API](tools/documentation_retrieval.md)
adds complete lexical helper quotes and durable integrity receipts. Neither
it nor the [Go build-filtered binding tool](tools/go-build-binding/README.md)
changes ordinary Ruby routing or proves general runtime semantics.

The [default-claim review](research/documentation-intelligence-20261119/default-claim-ambiguity-evaluation.json)
refuses ambiguous concatenated parameter/default text and supports an explicit
delimiter. A [separate module-binding correction](research/documentation-intelligence-20261119/python-registry-binding-evaluation.json)
prevents false retirement recommendations when a registry and function share
one Python binding. Earlier incorrect recommendations are retained and were
never applied to active documentation.

The [navigation experiment](research/documentation-intelligence-20261119/candidate-navigation-evaluation.json)
uses the actual unchanged Markdown/navigation functions on an isolated catalog.
All 77 reviewed question pairs now share explicit navigation identities.
Two sequence diagrams passed Mermaid parsing; four flowcharts remain unverified
because plain Node lacks the required DOM environment. Forty-two research
references also need an explicit reader/source-asset policy before publication.
The active catalog and reader UI remain unchanged.

The new campaign has completed 42 local model requests so far: 24 original
lifecycle baselines, two adapter calls and 16 paired decision-form experiments.
The [new paired study](research/documentation-intelligence-20261119/decomposed-decision-evaluation.json)
did not demonstrate improvement: direct actions matched four of eight references
and included one critical false removal; predicate decomposition matched one
and abstained on every case. Several PT-BR reasons were corrupted. No returned
prose or JSON schema pass was promoted into publication or training approval.

The [current local recovery cut](research/documentation-intelligence-20261119/current-operational-recovery.json)
independently restored 485 operational files plus their recovery manifest.
All 137 new Python tests passed from the restored tree on macOS and on the
existing Linux runtime. A separate new model store reconstructed the approved
weight and metadata hashes from the preserved parts; the original store was
verified and left intact. The restored store was not served or used for a new
inference. These are dated same-host checks, not remote disaster recovery.

The private [Git LFS 3.8.1 recheck](research/documentation-intelligence-20261119/git-lfs-current-local-validation.json)
roundtripped that code capsule through a private local object store and compared
all 810 current Git metadata files unchanged. No installation, hooks, filter
configuration, staging or uploads occurred. The older absence statement above
describes its historical preflight; private tooling is now available. Remote
storage, accepted artifact paths and off-host recovery remain unverified.


## Further verified research cut — 2026-11-20, 04:25 UTC

The earlier supplement remains a dated source cut. The current lifecycle tool is
0.3.4: its CLI rejects ambiguous duplicate JSON fields, nonfinite values, invalid
Unicode and unstable, oversized or special-file inputs. The preserved old CLI
could recommend REMOVE after a repeated source field masked a present function;
the new boundary refuses that raw packet without creating a candidate. A FIFO
that blocked the old CLI is refused immediately. Canonical development decisions
remain 22/24, with the same two default JavaScript refusals. See the
[raw-boundary comparison](research/documentation-intelligence-20261119/packet-json-boundary-evaluation.json).
The current Python suite passed 194 tests; the older 137-test restored cut above
remains a separate, explicitly dated recovery observation.

The optional [closed Python dependency observer](tools/documentation_python_dependencies.md)
resolves narrow zero-argument integer-return chains and conservatively binds all
registered source hashes. Its twelve synthetic cases match their references;
four cross-file cases are newly resolved relative to the root-only profile.
The optional [durable helper budget](tools/documentation_job_budget.md) retains
reservations across instances/processes, suppresses unknown replay and withholds
late or unaudited quotations. Six concurrent processes respected a two-step
allowance. Neither API changes the ordinary Ruby route or proves general bindings.

The [current raw-response ledger](research/documentation-intelligence-20261119/inference-current-ledger-v2.json)
reconciles 52 complete responses and 5,376 generated tokens. Six are literal and
arithmetic controls, and four test closed-fact documentation. The controls refute
a universal inability to emit true, but only three of six are entirely correct.
The four-documentation comparison still shows no generated-answer gain from the
closed facts. All 52 pass the exact observed schema constraints; that does not
repair their retained factual or bilingual failures. No optimizer step occurred.

All six exact candidate diagrams were rendered in an installed browser and the
six images were visually inspected. The [browser receipt](research/documentation-intelligence-20261119/mermaid-browser-evaluation.json)
separates this result from earlier Node DOM and premature capture failures.
A separate [reading proposal](research/documentation-intelligence-20261119/reader-bundle/en/README.md)
with a [Portuguese index](research/documentation-intelligence-20261119/reader-bundle/pt-br/README.md)
provides 50 chapter derivatives and 50 exact artifact views. Its 164 local links
actually load, and all 77 FAQ identities remain shared. Only link destinations
changed in the copied chapter bodies. The active catalog/UI and original 50
candidates remain unchanged. These derivative files are not independent examples.

The new [private evidence capsule](research/documentation-intelligence-20261119/source-evidence-recovery.json)
restored 1,958 complete source/evidence files. An additional
[content snapshot](research/documentation-intelligence-20261119/dataset-reference-preservation.json)
retains 357 unique blobs for dataset/source references, independently recovered
without reading original paths. The installed Ollama image was also saved and
its Linux/arm64 content closure verified without loading or starting it. The
amd64 platform advertised by its index is not included. Remote recovery remains
unverified. The dataset V2, self-chapter and first reader proposal predate the
0.3.4 raw-boundary change; [source-cut evolution](research/documentation-intelligence-20261119/source-cut-evolution.json)
preserves those exact prior bytes pending the next current review cut.


### Dated current research cut — 20 November 2026, 05:40 UTC

The earlier supplements remain historical observations. The current raw ledger
contains 56 complete responses, 5,640 generated tokens and 1,956.070655435 server
seconds. Four later representation controls did not recover the supplied closed
facts; the presentation-retry line was stopped. JSON shape validity did not
establish factual correctness, and no training or optimizer step occurred.

The closed dependency observer is now 0.1.2 and helper retrieval is 0.1.3. Both
pin operation configuration after two reproduced mutable-registry defects.
The [guard evaluation](research/documentation-intelligence-20261119/frozen-registry-guard-evaluation.json)
preserves the pre-fix failures and corrected controls. The optional closed FAQ
renderer prepares one conditional integer-return question in memory with no model
or document write; its eight fixture pairs are separate from the 77 chapter FAQs.

The [current dataset V3](research/documentation-intelligence-20261119/datasets/v3/manifest.json)
has 305 records with immutable direct references. The previous V2 stays intact.
The 56 responses come from 55 distinct request contents; two root-only controls
intentionally shared the same request. Twelve cachetools structural references
are test-only and never approved training targets. The
[family-exposure ledger](research/documentation-intelligence-20261119/cachetools-family-exposure-ledger.json)
separates the fixed helper evaluation from later development on that source.

The [updated reader proposal](research/documentation-intelligence-20261119/reader-bundle-v2/en/README.md)
and [Portuguese index](research/documentation-intelligence-20261119/reader-bundle-v2/pt-br/README.md)
contain 116 derived documents and 192 actually loaded local targets. Non-link
chapter bytes and 77 shared FAQ identities are preserved; the active catalog is
unchanged. Twenty-one existing FAQ pairs now have manual claim-to-source
annotations covering 36 physical spans; 56 pairs still lack that finer annotation.

The optional [revision signal API](tools/documentation_revision_signals.md)
compares supplied Python module/declaration ASTs and always leaves the document
action unset. Fifteen controls cover source ownership, helper-only changes,
multiline strings, type comments, unknown declarations and failure boundaries.
The complete current suite passed 228 tests. Five real cachetools revision
references matched the structural signals, while the existing restricted
lifecycle planner safely abstained on all five. Manual ADD/MODIFY/NO-OP proposals
were not applied by bypassing that refusal.

A [dated 796-file operational capsule](research/documentation-intelligence-20261119/operational-recovery-current-v2.json)
passed knowledge checks and the earlier 213-test cut after independent extraction
on macOS Python 3.14.7 and existing Linux ARM64 Python 3.11.2. It predates the new
revision signal tool. An initial Python 3.9.6 discovery failure remains recorded.
The [private artifact catalog](research/documentation-intelligence-20261119/private-artifact-catalog-receipt-v1.json)
individually pins 4,907 regular ignored research artifacts plus a symlink and two
sealed runtime manifests. Weights, image closure, source evidence and code remain
separate recovery components; no remote restore or new model-serving test is
claimed. All additions remain unstaged and pending owner review.


### Typed-input consistency correction — 2026-11-20T06:40:54.627353+00:00

The [current six-path study](research/documentation-intelligence-20261119/typed-input-snapshot-evaluation-v2.json)
reproduced and prevented caller-dictionary drift across the direct lifecycle
planner, memory candidate editor, owned workspace builder and restricted FAQ
maintainer. Planner 0.3.5 and the three 0.1.1 APIs use per-call input copies. A
correct MODIFY recommendation can no longer be changed into an isolated REMOVE
by editing the caller's action after validation. Changed source hashes cannot
replace the registered inventory during final rechecks. The workspace requires
an explicit Boolean `prepare` argument.

The current local Python suite passed 238 tests. The same frozen canonical matrix
still matches 22 of 24 actions, with two safe JavaScript abstentions; the six new
adversarial cases are separate from that matrix. New explicit valid operations
and replans remain supported. Original files were not changed by those controlled
experiments, and no model call or optimizer step occurred.

The [implementation safety ledger](research/documentation-intelligence-20261119/implementation-safety-cut-ledger.json)
marks prior implementations as unsuitable for current use under mutable callers.
Earlier capsules remain verified recovery evidence; their old test passes do not
certify the later-discovered failure paths. The repaired code remains optional
and pending owner review. Default Ruby routing, active catalog and production UI
remain unchanged.

### Documentation intelligence supplement — 2026-11-20 07:23 UTC

The optional owned-workspace CLI0.1.2 now admits stable regular bounded JSON
specifications; a reproduced FIFO hang and six boundary controls are preserved
in [the admission study](research/documentation-intelligence-20261119/maintenance-spec-boundary-evaluation.json).
The optional [conditional FAQ revision API](tools/documentation_conditional_faq_revision.md)
0.1.0 plans exact paired-record ADD/MODIFY/NO-OP or INCONCLUSIVE from fresh
closed dependency snapshots. It retains the runtime-binding caveat, never
recommends REMOVE and changes no ordinary Ruby routing or original documents.
Its sixteen owned development references matched; the combined264-test suite
also passed from independent macOS/Linux restored copies in
[operational cutV5](research/documentation-intelligence-20261119/operational-recovery-current-v5.json).
Earlier weaker cuts remain historical recovery evidence, not current safety
certification. Owner approval, publication and training gold remain separate.

### Physical document and output consistency — 2026-11-20 08:42 UTC

Candidate construction0.1.2 now binds NO-OP to the addressed physical block,
its expected checksum and the exact packet claim. Two real false NO-OP reports
were reproduced while the physical documents remained stale; corrected inputs
refuse without changing originals. See the [NO-OP study](research/documentation-intelligence-20261119/noop-document-binding-evaluation-v1.json).

Owned workspace maintenance0.1.4 also verifies the new output root, active/history
inventories and bytes, preserved mode/mtime, preconditions and the durable result.
Five controlled output mutations previously produced false preparation success;
all now refuse in fresh equivalent workspaces, while a valid candidate succeeds.
The [output study](research/documentation-intelligence-20261119/candidate-output-closure-evaluation-v1.json)
preserves partial artifacts and the earlier code. Sequential checks are not an
atomic transaction against writers after the final check. A result file alone is
not completion, owner approval or permission to publish.

The [current operational cutV7](research/documentation-intelligence-20261119/operational-recovery-current-v7.json)
restored1,713files and passed all278tests on macOS and existing LinuxARM64.
The [candidate API guide](tools/documentation_candidates.md) documents both
boundaries. Earlier264/271-test cuts remain dated recovery evidence. No ordinary
Ruby routing, model weight, active catalog, Git index or publication changed.
