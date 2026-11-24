# Local documentation command

Engineering Library is private. Enter its existing backend with `docker compose exec backend sh`, then run `make docs`. The current caller is version 1.9.12, uses the Rails bundle and explicitly calls the Docker Ollama service. The configured default is `llama3.2:3b`; model selection is never silently replaced. Output is an unreviewed bilingual source-summary draft, not autonomous factual approval.

## Docker-only preparation

Run these Docker CLI commands from this repository. No host Python, Bash, Ruby, Node or make is required. The one-off setup helper temporarily receives a writable sibling collection solely to create missing `docs/` directories; it preserves existing contents and assigns new directories their parent's owner. Normal generation mounts source read-only and only each documentation destination writable.

```sh
docker compose run --rm --no-deps --user 0:0 --volume ..:/sources --entrypoint python3 backend /sources/engineering-library/tools/prepare_docs_mounts.py --bind-root /sources=.. --output /docs/.docs-state/setup
docker compose -f compose.yaml -f docs/.docs-state/setup/mounts.json config --quiet
docker compose -f compose.yaml -f docs/.docs-state/setup/mounts.json up -d --no-deps backend
docker compose exec backend sh
# Inside the backend:
make docs
make docs DOCS_ARGS='--project project-slug'
```

Mounts cannot be added with `exec`: applying this overlay recreates only the backend. Preserve existing configuration, environment, volumes and data. For an already prepared source set, generation needs no setup recreation. The helper's optional host-Python invocation remains a convenience, not a dependency.

Default discovery visits direct sibling Git repositories only. It excludes this library, symlinks and nested vendor/tooling checkouts; it never walks unrelated ancestors. Additional collections are explicit installation configuration. Mount a second collection at `/extra-sources-1` during setup and pass a second `--bind-root /extra-sources-1=RELATIVE_COMPOSE_SOURCE` (or an absolute host path); retain that mount in the generated overlay. Relative sources resolve against the first Compose file. Paths containing spaces must be quoted by the invoking shell. Do not publish the generated selection as a portable agent dataset.

Use the generated `/docs/.docs-state/setup/projects.json` or a private JSON selection:

```sh
make docs DOCS_ARGS='--config /docs/.docs-state/setup/projects.json'
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug'
```

```json
{"projects":[{"slug":"project-slug","source":"/sources/project-slug","destination":"/project-docs/project-slug","files":["src/component.rb"],"question":"Explain the declared contract and its failure boundary."}]}
```

`files` and `question` are optional. A question is an explicit task, not verified evidence. Default selection is bounded to four complete eligible files and 6 KiB total for CPU inference. Explicit `files` selections retain up to twelve files and 24 KiB; any eligible file is at most 64 KiB. Oversized automatic candidates are omitted and counted, never silently truncated. The smaller default follows observed 300-second timeouts with the earlier 24 KiB automatic sample; it trades breadth for a bounded draft, not exhaustive architecture coverage. Missing explicitly selected files fail the project. Hidden files, dotenv, credentials, dependencies, generated/runtime data, tests and `docs_codex` are excluded. Recognized credential literals cause omission, or rejection when explicitly selected. This is a conservative guard, not comprehensive secret detection; review selected evidence before authorizing an audit or research task.

## Evidence and skills

The caller reads exact current source bytes through read-only mounts. `DOCS_EVIDENCE_MODE=declarations` is the default: simple Rust enums and bounded inherent public-method excerpts receive deterministic preparation. Unsupported forms fall back to raw excerpts; `DOCS_EVIDENCE_MODE=raw` explicitly selects the earlier representation. This assistance is recorded and must not be credited as autonomous model discovery. Partial sampling does not establish full architecture coverage.

Evidence, authoring and review skills are explicitly loaded from `agent/skills/`; hashes enter the fingerprint. Their concise English system context drives generation, with equivalent Portuguese operational guidance retained. The MIT upstream attribution is preserved; the deleted upstream checkout is unnecessary. `DOCS_CONTEXT=baseline` omits these skills for controlled comparisons. `DOCS_TRANSPORT=generate` is an experimental alternative; chat is normal. Repeated inference does not train model weights. Each actual request uses `keep_alive=0` to release the model runner after completion while preserving the Ollama service. This adds reload latency and is not a guarantee against OOM. The 16k context is resource intensive; do not overlap inference with browser/media or application builds when memory is constrained. Inspect failures and actual resource use rather than inferring a cause from a historical OOM flag.

One local response supplies both languages. The caller validates completion, JSON/schema, evidence IDs, exact source excerpts, selected symbol constraints and basic formatting. These checks do not establish factual accuracy, useful depth or semantic translation parity. The 3B model has produced wrong responsibilities, invented defaults and unsupported integration claims. Keep generated drafts visibly unreviewed until a human checks both languages against source/runtime evidence.

For an explicitly assisted revision, optional `feedback` has exactly `kind` (`reviewer-feedback` or `codex-reference`), `source_hashes` (the current selected file path to SHA-256 map) and bounded `text`. Stale hashes reject before inference. The output and manifest label assistance. Initial independent evaluation excludes references and reviewer conclusions; assisted revisions are separate results, never autonomous successes. `docs_codex` is not automatically loaded.

## Optional public web research

Offline is the default. Local inference remains local. Optional SearXNG is an AGPL-licensed self-hosted search path without required API credentials; upstream engines may throttle, challenge or fail. It is not an unlimited or guaranteed service.

```sh
docker compose -f compose.yaml -f compose.research.yaml --profile research up -d research
# Inside backend, with an explicit public research configuration:
DOCS_RESEARCH=search make docs DOCS_ARGS='--config /tmp/projects.json'
DOCS_RESEARCH=urls make docs DOCS_ARGS='--config /tmp/projects.json'
DOCS_RESEARCH=offline make docs DOCS_ARGS='--config /tmp/projects.json'
```

```json
{"research":{"technology":"Ruby","version":"3.4","query":"Ruby 3.4 Net HTTP ipaddr documentation","primary_hosts":["docs.ruby-lang.org"],"urls":[],"max_sources":1,"version_pattern":"3.4"}}
```

Place that `research` object inside the selected project object. URLs mode fetches up to two explicitly approved public URLs; search mode discovers candidates and fetches only approved primary hosts. Queries require reviewed public technology/version/topic words; private project names, source code, personal data, credentials and arbitrary identifiers must not be sent. Queries are explicit, never inferred from source. Unknown words are rejected rather than sent.

Public fetches allow HTTP(S) on standard ports only. DNS addresses and every redirect are checked; private, loopback, link-local, metadata and reserved addresses are rejected, and connections pin validated IPs while preserving TLS hostname checks. Requests have bounded time, bytes, content type and redirects. Downloaded content is parsed as untrusted text and never executed. Version-pattern matching is a narrow filter, not semantic version compatibility proof.

Research emits source URL, consultation time, small quoted passage and its hash. A separate local call sees only public passages; the source-analysis call sees no web packet. Public documentation explains a technology contract and cannot prove local implementation. Bad public prose is rejected; retained exact passages remain clearly labeled. Search/fetch outages yield explicit degraded status and preserve local generation. Offline makes no research requests. `DOCS_RESEARCH_REFRESH=1` deliberately refreshes opt-in consultation; otherwise matching inputs can reuse their owned result. `DOCS_SEARCH_URL` is restricted to the local `http://research:8080/search` boundary.

Model provisioning is a separate, intentional download, not part of generation:

```sh
docker compose exec ollama ollama list
# Only when the owner intentionally provisions that model:
docker compose exec ollama ollama pull llama3.2:3b
```

## Dual destinations and navigation

| Library | Analyzed repository |
| --- | --- |
| `docs/<slug>/en/guides/generated-source-summary.md` | `docs/en/guides/generated-source-summary.md` |
| `docs/<slug>/pt-br/guides/generated-source-summary.md` | `docs/pt-br/guides/generated-source-summary.md` |
| `docs/<slug>/img/` | `docs/img/` |

Language-specific summary copies are byte-identical from the same response. Each localized index receives an owned draft link inside `make-docs:source-summary` markers. The command owns those blocks, its dedicated summaries and library `.docs-state` metadata, preserving human text outside blocks. It does not invent bios/icons, synchronize database catalog records, generate raster images, run applications or query project databases. Accepted actual screenshots/diagrams can be prepared separately and shared between destinations; text inference does not generate pixels.

The journal covers all four summaries plus four index files. Existing unowned summaries, human edits inside owned content, unwritable destinations or pending recovery reject the project. Human additions outside managed index blocks are preserved. Missing source/mounts never imply deletion. Current source changes regenerate the owned result; check obsolete claims manually. Unchanged relevant inputs and owned content produce no-op without inference or rewriting. Per-project failures are reported while other selected projects continue.

## Recovery and evidence retention

A library-wide lock serializes runs. Source/ownership preflight occurs before inference and again before application. Candidates and backups are hashed; writes use per-file atomic rename/fsync and a persistent journal. This is not a cross-filesystem atomic transaction. After interruption, use the SAME destination configuration:

```sh
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug --recover rollback'
# Or after reviewing the saved candidates:
make docs DOCS_ARGS='--config /tmp/projects.json --project project-slug --recover complete'
```

Rollback restores prior owned bytes and manifest; completion uses saved candidates without inference and rejects changed sources. Recovery checks current bytes and preserves concurrent edits; retain the journal/backups when blocked. Never delete owner data, volumes or unrelated documentation to clear an error.

`DOCS_AUDIT=1` emits exact source/request/response events to stdout. Preserve experimental outcomes and failures in private operational storage; reusable examples require separate review before entering the active agent tree. Keep secrets, runtime weights/caches/dependencies and recovery backups excluded; do not delete recovery state for cosmetic cleanup. Actual project documentation retains correct identities. Earlier committed names remain in history; no anonymity or release-readiness certification is implied.

Current evidence distinguishes simulated failure tests, real local inference, component execution, full builds and actual application/browser checks. Execution is on a macOS host with Linux Docker containers; Android uses an emulated AMD64 image. Windows/WSL2 and an independent Linux host remain unverified. Consult the current run report for project-specific coverage, rejected skill experiments and remaining factual errors.

## Temporary evaluations and original-documentation isolation

A project selection may explicitly set `"lifecycle":"temporary"`. Its library copies go to `docs/.evaluations/<slug>/`, and ownership/recovery state goes to `docs/.docs-state/evaluations/`. The analyzed-project destination remains its explicitly configured `docs/` mount. This setting does not authorize deleting pre-existing project documentation. Catalog synchronization ignores the hidden evaluation tree; `docs/.catalog-policy.json` additionally lists retired external project slugs that normal synchronization must not activate. Historical provenance is preserved separately from the current catalog.

The source collector excludes `docs_backup`, `docs_codex`, and their unique suffix variants, even with explicit file selection. The local model receives source cards and the three active skill contexts, not evaluation reports or preserved documentation. These directory guards cannot identify arbitrary undisclosed copies under unrelated filenames.

`tools/evaluation_lifecycle.py` provides `capture`, `seal`, and `restore` operations with an explicit private `--session` directory and repeatable `--root` arguments for capture. Capture inventories exact bytes and modes and preserves original files. Seal records the operator-reviewed experimental final inventory. Restore rejects conflicting edits and corrupt backups before writing, restores original files, and removes only the sealed additions. An interrupted restoration can be retried. The operator must establish file ownership before sealing; this tool does not infer authorship. It rejects symbolic links and retains recovery backups after restoration. It does not restore databases or services, and is not a cross-filesystem transaction.

## Experimental structural evidence

`DOCS_EVIDENCE_MODE=structural` opts into complete Python function/method ranges extracted through Python's standard AST parser. Python must be available inside the backend container; application modules are never imported by this parser. Exact source excerpts and line positions are retained. Functions over the 1,900-character quote bound are rejected rather than split. Class ownership is a syntax hint, not call-chain or runtime proof. Other languages retain the existing representation, including Java; C/C++ source/header extensions are now eligible within the existing file/context bounds. This mode is experimental and does not replace the default `declarations` mode or establish superior factual/bilingual quality.

Raw `DOCS_AUDIT=1` output can contain authorized private source. Keep it in an access-controlled, Git-ignored operational directory such as the existing `.local-backups/`, not the active reusable `agent/` tree. A public reusable example requires separate content and provenance review; neutral names alone do not establish anonymity.

## Uniqueness-claim rejection

A narrow lexical guard rejects affirmative uniqueness claims when the cited excerpt contains no explicit uniqueness constraint. It recognizes a bounded set of EN/PT-BR negations and explicit `UNIQUE`, `PRIMARY KEY` or `unique()` constructs. This is rejection assistance, not a semantic proof: a matching word/construct can have the wrong scope, and many other factual errors remain undetected. Legitimate claims requiring broader evidence may also be rejected. Schema-valid output still requires factual/bilingual review. The guard was introduced in 1.9.3. Caller-version changes invalidate the fingerprint, so an older cached draft is not treated as validation by the current caller.

## Explicit complete units

An experimental project `units` map can select complete definitions within explicit `files`. For example, `"files":["src/math.cpp"],"units":{"src/math.cpp":["Vector2Lerp"]}` sends only that selected definition as source evidence. Selectors may use an unambiguous short name or its qualified owner name. Missing, ambiguous or unsupported definitions reject before inference. The question remains an authoring task, never proof.

Python selection uses AST ranges. C, C++, Java, PHP, Rust and supported Go free functions use a conservative definition-layout lexer that masks comments/literals and tracks enclosing scopes. It is not a compiler or semantic parser: templates, macro expansion, generated methods, some language layouts and conditional definitions require separate inspection. Only explicitly selected definitions are included; dependencies and fields are not discovered automatically. A class/namespace ownership hint does not establish runtime behavior.

For selected-unit files, the caller reads at most 1 MiB per file for full-file hashing, change detection and credential screening, while only selected quotes enter the model source cards. Each complete unit is bounded to 6,144 characters, with at most twelve selected units and 24 KiB total selected source context. Other files retain the earlier bounds. Full-file hashes identify the revision; they do not mean the model saw the whole file. Output marks this narrower scope. Backup/reference exclusions apply before selection and cannot be bypassed with `units`.

Short names with fewer than three characters require the qualified name in each explanation; other selected methods require their exact method name. The caller also rejects bounded patterns naming an absent type or assigning a method to another owner. These lexical checks can reject legitimate prose and miss semantic errors. Controlled trials still found invented bounds, argument-position mistakes and translation errors with complete units. This option improves source access and citation boundaries, not automatic factual acceptance.

## Current safeguards and installation limits

Version 1.9.7 retains the earlier uniqueness guard and adds bounded quoted-literal parity checks: selected short source tokens quoted in either language must remain exact in both explanations. Unquoted translated literals and broader semantic differences can still escape detection. Complete-unit coverage counts unique cited complete units, lists uncited units, and does not count raw file cards as complete definitions. Five selected units with four supported facts can therefore leave coverage incomplete. Neither counter is a quality score.

Go extraction supports conservative free-function layouts, including qualified parameter types and masked raw strings. Receivers, generics and anonymous return-type layouts are unsupported. Native parsing does not expand macros or resolve dependencies. Explicitly select helpers when a claim needs their bodies; the campaign still found wrong responsibility attribution and failure to describe changed arguments after adding call-chain context. Experimental Rust parameter-pairing remained private and was not promoted: it reduced one positional error by producing vague output that missed the controlled change.

The mount preparation helper excludes the ten temporary slugs in the validated catalog policy. Normal generation rejects those projects unless `lifecycle` is explicitly `temporary`. A legacy temporary journal may be rolled back; completing it through the permanent lifecycle is rejected. Invalid or symlink policy files fail closed.

Renaming a host `docs/` directory while a container runs can leave its narrow bind mount attached to the renamed backup inode. The caller rejects a narrow destination that is not identical to the current source `docs/` directory, including recovery, before writing. Archive any needed backend tmpfs evidence, finish running jobs, regenerate the installation overlay, and recreate only the backend with the preparation commands above. This rebinds the current directory; it does not restore files or databases. Confirm destination identity after recreation. Do not point a generation destination at `docs_backup/` to bypass this check.

## Shared-host inference profile and method extraction (1.9.11)

`DOCS_CONTEXT_TOKENS` selects 4,096–16,384 context tokens; the default remains 16,384. `DOCS_MODEL_THREADS` optionally selects 1–16 inference threads; omission preserves the server default. `DOCS_REQUEST_TIMEOUT` selects a 60–1,800 second read timeout; the default remains 300 seconds. Context and thread settings enter the generation fingerprint. Changing only the transport timeout does not invalidate an otherwise valid no-op. The manifest records the timeout actually used by its generation.

For an explicitly authorized evaluation configuration, a constrained-host example inside the backend is:

```sh
DOCS_CONTEXT_TOKENS=4096 DOCS_MODEL_THREADS=1 DOCS_REQUEST_TIMEOUT=900 \
  make docs DOCS_ARGS='--config /path/to/authorized-evaluation.json'
```

This is a configuration example, not a universal memory or latency guarantee. Match threads to the allotted CPU quota and record actual memory, prompt/output tokens, duration and failures. Below the default context, the caller rejects a prompt whose UTF-8 content exceeds the selected context minus a 256-token allowance, using bytes as a deliberately conservative token upper bound. Some prompts that a tokenizer could fit will therefore be rejected. Select fewer complete units; no source is silently shortened to fit this profile. Existing environment files need not be edited.

Source discovery recognizes `.cs` and `.gd`. Explicit complete-unit selection additionally supports ordinary C# methods and a bounded C++ class-template method form with one `class`/`typename` parameter and a single identifier template argument. The quote includes the template declaration; the canonical owner removes that argument, for example `Vector3::Normalize`. This is lexical source selection, not Roslyn/C++ semantic analysis. Free function templates, specializations, nested/multiple template parameters, requires-expressions, properties, macro expansion and ambiguous definitions remain outside this bounded method support. GDScript recognition does not add a GDScript AST selector.

Named reviewer-feedback, expected-output, comparison-summary and Codex-reference files/directories are excluded before explicit selection. This convention does not detect arbitrarily renamed answers. Inspect captured requests to verify the actual evidence boundary. Exact quotes, schema validity and successful writes remain separate from factual and bilingual acceptance; a translation can still replace a signed difference with an incorrect absolute value.

The separate `tools/documentation_similarity.py` evaluator consumes frozen bilingual artifacts and source-reviewed claim judgments. It checks source-file and cited-span hashes, reports the five weighted dimensions separately, and leaves missing dimensions incomplete. Copied source quotations do not contribute to textual similarity. Its reproducible heuristics do not prove semantic truth, complete project coverage, owner approval or readiness to remove recoverable backups. Operational results belong in the dated evaluation report.

## Explicit multi-section project drafts

Caller version 1.9.12 fixes demonstratives such as “This class” being mistaken for an invented type; explicitly named foreign types remain rejected. The optional project coordinator is version 1.0.1. Its four-section campaign produced real bilingual drafts, but factual errors and omitted contracts prevented complete-project acceptance. A successful write or exact source citation is not factual approval.

Inside the existing backend, provide an explicit private plan and separate persistent writable library/workspace directories:

```sh
DOCS_LIBRARY=/docs/.evaluations/my-run DOCS_WORKSPACE=/docs/.docs-state/workspaces/my-run DOCS_CONTEXT_TOKENS=4096 DOCS_MODEL_THREADS=2 DOCS_REQUEST_TIMEOUT=600 DOCS_RESEARCH=offline make docs DOCS_WORKFLOW=project DOCS_ARGS='--config /docs/.docs-state/my-plan.json --project sample'
```

The plan has `schema: 1` and `projects`. Each project requires a validated `slug`, `name`, read-only `source`, frozen Git `source_revision` and `sections`. Each section requires an `id`, bilingual `titles` (`en`, `pt-br`), `files`, `question`, and either inclusive original-file `ranges` (path to arrays of `[start, end]`) or supported complete `units` (path to exact identifiers). Ranges are source-layout selections, not semantic AST proofs. Model excerpts are bounded; oversized context is rejected rather than silently truncated. Exclude generated documentation, independent references, credentials and owner environment files from source selections.

The coordinator copies the selected original files into its owned workspace, records full-file hashes, checks the frozen revision, uses the existing transactional section command and records durable per-section audit logs under `audits/SLUG/SECTION.ndjson`. A nonblocking library lock prevents a second project coordinator writing the same root. Transport failure aborts before scheduling another section. A rejected section stays explicitly rejected; a failed revision preserves an existing assembled draft. Bilingual assembly checks both destinations before writing and retains a pending journal on interruption. Inspect and recover a pending journal before another write; automatic recovery after restart is not promised.

Project drafts are assembled in `DOCS_LIBRARY/projects/SLUG/{en,pt-br}.md`; child outputs, ownership manifests and audits remain separate. Original repository `docs/` paths are unchanged when destinations are the isolated staging copies. Use durable host-backed locations for resumable work: the backend `/tmp` and `tmp` campaign workspaces can be ephemeral. Preserve a private archive, raw responses, selected source files and notices before retiring evaluation trees with the capture/seal/restore lifecycle tool. Do not delete whole repository documentation trees or stop normal Library/Viva Bem services for cleanup.

The source-only metadata-view and source-reviewed proposition candidates from the ten-repository evaluation remain private experiments. They are not enabled by this workflow. Keep independent generation, reviewer-assisted variants and complete-project acceptance distinct.
