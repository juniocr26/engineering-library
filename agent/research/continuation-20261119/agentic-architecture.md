# Agentic architecture investigation — 2026-11-19

Status: research and source inspection; proposed tool experiment requires a separate implementation decision. No MCP server, plugin package, new harness, or production routing is installed by this workstream. No neural training has occurred.

## Scope and evidence

Baseline: `engineering-library`, `main`, HEAD `fe2d062f7c791fa35288929bf27c7c1cf2055bf8`. Runtime source is the authority; the previous campaign report is historical. The requested study PDF was not found in the attached files or the searched Documents tree (depth five). This does not establish its absence from every connected service. The two supplied campaign texts define the accessible research brief.

Evidence identifiers below name repository paths and method names, so findings remain navigable after line changes:

| ID | Inspected evidence | Meaning |
| --- | --- | --- |
| E1 | `backend/Makefile`, `backend/lib/documentation/command.rb`: `run`, `process`, `infer`, `source_model_request`, `call_model` | Actual normal entry point and inference path |
| E2 | `backend/lib/documentation/project_command.rb`: `ProjectCommand#run`, `process`, `assemble`, `SectionCommand#evidence` | Explicit project/section orchestration and isolated draft assembly |
| E3 | `backend/lib/documentation/command.rb`: `evidence`, `source_units`, `evidence_cards`, `python_fragments`, `rust_fragments` | Bounded source preparation |
| E4 | `agent/tools/go_source_ast.py`: `executable`, `run`; `agent/tools/go-source-ast/main.go`; `backend/lib/documentation/go_ast_command.rb` | Optional verified syntax producer and Ruby consumer |
| E5 | `agent/tools/javascript_ranges.cjs`, `javascript_leading_guard.cjs`; `backend/lib/documentation/python_structure.py`, `python_async_facts.py` | Optional language profiles; syntax does not establish imported helper semantics |
| E6 | `backend/lib/documentation/command.rb`: `skill_context`; `agent/skills/{evidence,authoring,review}/SKILL.md` | Three fixed source contexts loaded into prompts |
| E7 | `backend/lib/documentation/command.rb`: `validate_and_render`, `safe_paragraph?`, `unsupported_called_symbol?`, `source_backed_delegated_return?`, `quoted_literal_mismatch?` | Deterministic acceptance guards, with explicit factual limits |
| E8 | `backend/lib/documentation/command.rb`: `atomic`, `check_ownership`, `recover`, `preserve_attempt_artifact`, `source_unit_cache_key` | File ownership, journals, attempts, no-op and exact-context reuse |
| E9 | `backend/lib/documentation/research.rb`: `validate_url`, `resolve`, `request`, `collect` | Optional public research, constrained networking, deadlines |
| E10 | `agent/recovery/{bootstrap.py,bundle.py,manifest.json,model-bundle.json}` | Local model/operational integrity and independent restoration mechanisms |
| E11 | `.local-backups/continuation-20261119/baseline-ruby-tests.log`, `recovery-knowledge-after.json`, `baseline.json` | Current executed baseline and recovery checks; private artifacts |

## Current execution map

```text
owner-selected config / make docs
  -> Command.run: validate settings, acquire nonblocking filesystem lock
  -> validate_project: source/destination containment and selection policy
  -> process: collect source, fixed skills, model identity, fingerprint
       -> check owned outputs; unchanged input returns no-op
       -> preserve private generation input
       -> optional controlled public research
       -> exact-context result reuse OR bounded Ollama HTTP inference
       -> preserve result; validate schema, evidence references and paragraphs
       -> re-read source; reject concurrent change
       -> stage candidate/before bytes; journal; atomic output updates
       -> save manifest and remove pending journal

explicit project plan
  -> freeze-check source HEAD
  -> at most 12 declared sections
  -> owned isolated source copies -> SectionCommand -> draft assembly
  -> independent factual review still required
```

This is application-directed orchestration. No inspected model request exposes callable tools or processes a model-selected tool call. The Go producer is a subprocess selected by application code. The optional public research client is also application selected. Successful JSON validation does not prove complete or correct prose.

## Capability and gap matrix

`ABSENT` means absent from the inspected execution path, not a claim about every file or future branch. `CONFIRMED` can describe source inspection; executed evidence is called out separately.

| Capability | Status | Evidence and limitation |
| --- | --- | --- |
| Application-controlled inference loop | CONFIRMED | E1/E2: per-project/per-section loops; not an autonomous planner |
| Ollama chat/generate transport and digest enforcement | CONFIRMED | E1: `call_model`, `verify_model_identity`; current tags report approved digest |
| Model-controlled tool dispatch | ABSENT | E1 requests use source messages and output schema; no tool-call dispatch in this path |
| Exact selected-source excerpts and provenance | CONFIRMED | E3/E4; byte/hash/span checks; syntax-only scope explicit |
| Cross-file semantic dependency resolution | ABSENT | E3/E4: explicit files/units; Go parser receives source text, not a module graph |
| Go module-aware import resolution | ABSENT | E4 parses syntax; `go.mod` being selectable in E1 is not module resolution |
| Fixed source-authoring skills consumed | CONFIRMED | E6 loads three fixed paths and context blocks |
| Agent Skills format and progressive discovery | PARTIAL | E6 contexts lack required YAML metadata; no metadata discovery/activation path inspected |
| Native MCP host/client/server in documentation path | ABSENT | E1/E2/E4/E9 use HTTP or subprocess interfaces, not JSON-RPC MCP methods |
| Agent Plugins client/package conformance | NOT VERIFIED | No conformance validation executed; existing three contexts do not establish a plugin implementation |
| Context and output bounds | CONFIRMED | E1: bounded files/bytes, 4096–16384 context setting, 1800 predicted tokens, 1–5 facts |
| Whole-run execution deadline | PARTIAL | E1 per-request read timeout; no end-to-end campaign/section wall deadline established |
| Cancellation | PARTIAL | E2 interrupt prevents later sections; termination of remote inference after transport interruption not verified |
| Retry/idempotency control | PARTIAL | E8 local locks/journals/no-op; remote inference completion after an ambiguous failure has no durable request reconciliation |
| File mutation permission boundary | CONFIRMED | E1/E8 restrict source/docs destination and preserve human edits; E11 tests run |
| Per-tool authorization policy | ABSENT | No model-selected tool dispatcher exists to enforce such a policy |
| Prompt-injection resistance | PARTIAL | E1 labels source untrusted, E7 checks outputs; adversarial semantic robustness is not established |
| Tool input/output validation | PARTIAL | E4 validates producer identity/spans; not a general tool schema/permission system |
| Durable local generation attempts | CONFIRMED | E8 persists input/result independently of console verbosity |
| Crash recovery for output application | CONFIRMED | E8 journals and checks conflicts; existing offline suite covers interruptions |
| Automatic semantic dependency cache invalidation | ABSENT | E8 hashes the prepared request; helpers outside selected evidence are not discovered |
| Relevant explicitly selected helper invalidation | CONFIRMED | Existing `documentation_source_reuse_offline.rb` includes selected-helper change regression |
| Runtime consumption of research JSON | ABSENT | E6 consumes fixed skill text; archived research is not automatically prompt context |
| Local operational recovery | CONFIRMED | E10/E11: repaired historical-report path passes all 117 knowledge hashes |
| Remote model recovery | NOT VERIFIED | No remote upload/publication or remote restore executed |

## Risk-ranked opportunities and ownership

1. High: incomplete selected evidence can produce confident documentation. A reproduced instance silently omitted invalid UTF-8/NUL helpers in ordinary `Command#evidence`; continuation caller 1.9.36 now refuses explicit invalid source. This is integrated independently of the proposed agentic experiment. The application owns the refusal; the model cannot repair missing bytes.
2. High: omitted valid helpers and unresolved ownership remain a factual risk. First compare explicit internal retrieval/selection against the baseline. The tool owns exact symbol/range retrieval and provenance; the harness owns allowlists, budget, timeout and deduplication; the model must preserve uncertainty and the evaluator must check the complete contract.
3. High: source comments or external pages can contain instructions. Retrieved text remains data. The application supplies trust separation and permissions; a tool description or skill cannot grant authority. Model compliance alone is insufficient.
4. Medium: cache reuse is exact-context reuse, not dependency-aware semantic validation. Select all necessary helpers now; propose explicit dependency provenance only when a controlled counterexample justifies it. Never silently retain a result after a required source changes or becomes unreadable.
5. Medium: ambiguous transport failures can consume duplicate inference work. Preserve raw events and inspect active requests before retry; no mutating model tools should be introduced without durable idempotency and reconciliation.
6. Medium: syntax inspection and a module/type resolver have different contracts. A module-aware Go resolver would need frozen `go.mod`/workspace/build constraints, import ownership, deterministic local-only resolution and safe refusal of unavailable modules. Do not claim package semantics from the current parser.
7. Low pending evidence: portable skills/plugin packaging may reduce duplication across compatible clients, but does not itself improve factual accuracy. Keep it a separately approved experiment.

## Comparative design: retrieve an exact helper

| Dimension | A. Internal bounded retrieval | B. Local MCP exposure | C. Investigation skill in Agent Plugins |
| --- | --- | --- | --- |
| Accuracy | Can add missing exact source; full-answer evaluation required | Same retrieval evidence; transport does not improve truth | Can teach evidence workflow; cannot supply absent code without a tool |
| Provenance | Reuse exact revision/hash/range checks | Preserve same packet inside validated tool output | Skill records procedure; underlying retrieval must still provide provenance |
| Complexity | Lowest fit with Ruby/verified subprocess path | Requires approved server/client, transport and capability/version policy | Requires compatible loader/package validation; optionally bundles B |
| Dependencies | Existing Ruby/Python/Go inspector where applicable | MCP implementation and local server lifecycle | Package metadata and supported client; tools remain separate dependencies |
| Security | Existing containment plus new explicit read-only allowlist | Same filesystem rules plus transport/server trust and process controls | Package containment, skill trust, tool permissions; packaging is not sandboxing |
| Interoperability | Internal interface | Standardized client/server boundary | Portable instructions and optional MCP configuration across compatible clients |
| Latency/resources | Measure extraction and prompt growth | Measure IPC/server overhead separately from inference | Instruction tokens and discovery overhead; no measured result yet |
| Maintenance | Smallest extension to current agent | Protocol compatibility and server lifecycle in addition to retrieval | Spec/client compatibility plus underlying retrieval maintenance |
| Current compatibility | Strongest architecture fit; still proposed if new routing | No existing documentation MCP consumer confirmed | Current fixed skill contexts are not a conformant loader/package |

These approaches can complement one another: an internal tool can become an MCP server capability, and a plugin can distribute the skill plus MCP configuration. Start with the smallest controlled internal experiment only after the separate decision required by this workstream.

## Primary specifications consulted

The live MCP latest URL redirected to **2026-07-28** during this research. Pin that version for a future experiment; do not silently use older lifecycle assumptions. Its overview defines JSON-RPC host/client/server responsibilities and distinguishes optional extensions. [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28).

For a proposed tool, follow the versioned tool request/response and schema contract. Safety annotations are not permission enforcement. [MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

Cancellation is transport-specific, and a timeout is not proof that work never happened. A future harness needs a maximum deadline and late-response policy. [MCP cancellation](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation).

Agent Skills specifies a skill directory with YAML frontmatter including `name` and `description`; `allowed-tools` is experimental. The client integration guide describes progressive disclosure; that guide is implementation guidance rather than proof that this repository implements discovery. [Format specification](https://agentskills.io/specification), [client guidance](https://agentskills.io/client-implementation/adding-skills-support).

Agent Plugins **1.0.0** identifies a portable package using root `plugin.json`, with skills and MCP configuration in fixed locations. Its normative sections differ from its non-normative appendix/design decisions; the specification takes priority over a conflicting schema. Package containment does not sandbox subprocess execution. [Agent Plugins specification](https://agent-plugins.org/specification).

## Recommendation and decision boundary

A possible future flow is `approved job -> frozen source registry -> bounded helper request -> validate permission/revision/schema/span -> deduplicate -> add untrusted source evidence -> one model inference -> complete-contract EN/PT evaluation -> owned isolated draft`. A refusal, exhausted budget or missing source stops that arm; it does not authorize a broader search. Retrieval and model inference have separate deadlines and audit events.

Two primary engineering accounts inform this recommendation without establishing a standard. Anthropic's long-running-agent article describes structured progress artifacts and incremental sessions; those principles fit the existing event ledger and checkpoints. Its example Git commit/revert workflow is inapplicable under this campaign's absolute Git restriction. [Anthropic account](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents).

OpenAI's harness-engineering account emphasizes making repository knowledge and feedback accessible to agents. Here, that supports explicit source ownership, reproducible evidence and verifiable acceptance criteria. It does not justify adopting the article's deployment, infrastructure or multi-agent arrangements, and its reported productivity is not evidence about this local model. [OpenAI account](https://openai.com/index/harness-engineering/).

Continue factual source selection and independent EN/PT review. Approve, if desired after review, one bounded internal retrieval prototype under the experiment plan in `helper-retrieval-proposal.json`. A decision must explicitly cover new retrieval dispatch, allowed repositories, output retention and regression cases. Separate decisions are needed for MCP server/client installation, plugin packaging/loading, module-resolution dependencies, or any production routing. None is authorized merely by completing these notes.

Research completed here: current execution map, capability inventory, primary-spec comparison, risk ranking and proposed experiment. Runtime architecture confirmed only where evidence above states so. Tool-driven experiment: proposed. Existing internal explicit-helper experiment: separate controlled comparison, not MCP. Harness improvement integrated: none. Neural training: none.


## Continuation evidence supplement — 14:50 UTC onward

The PDF search also checked connected Drive by the exact title and full filename,
with no matching PDF. A broader query returned unrelated DOCX metadata that was
not opened. This extends the initial local-search statement; it does not establish
absence from every account or location. See `pdf-access-check.json`.

The current caller is 1.9.38. The optional Go producer 1.5.0 adds one exact
callback/defer layout proof, consumed by a narrowly bounded refusal for the
observed order error. Python source-fact profile v3 additionally records a local
call assignment followed by an awaited return. These changes use existing
explicit profiles; they add neither autonomous retrieval nor MCP/plugin routing.
Their receipts distinguish language syntax from bindings and imported-helper
behavior. Current full checks passed 243 Ruby tests / 1,573 assertions and 36
Python tests. The original claims about ordinary-path architecture still apply.

The experimental responses show that successful writer acceptance can coexist
with wrong units, inverted maximum/minimum arithmetic, missing return values,
wrong protocol guards and invented exception propagation. Literal citations
and tool success must therefore remain separate from complete-contract approval.
The proposed second retrieval family in `helper-retrieval-family-extension.json`
is Go Image Optimizer quality normalization, with the numeric constant supplied
before helper retrieval. Existing smaller packets cannot be relabeled as that
baseline. Both proposed families are development material, not unseen holdouts.

A development Axum inference crossed an older reserved-family boundary. This
invalidated the current unused-holdout claim; the older dated reserve is preserved
and the incident is explicit in `holdout-reservation-incident.json`. The remaining
Axum state case has no direct output, but belongs to the same exposed family.
Future research scheduling must reconcile dataset reservations before selecting
from the queue. No intact independent reserved family or approved training split
is claimed. The training gate remains closed.

A deterministic whole-file credential check refused a Starlette URL task because
the file contains a literal password mask. The campaign retained the refusal
and did not weaken the guard or present rewritten source as original. Two Go
method selections refused by the legacy layout profile were explicitly rerun
through the already available Go AST profile after zero model calls. This was a
research configuration choice, not an automatic routing change.

## Continuation evidence supplement — 16:42 UTC cut

The source-preparation and orchestration changes remain inside existing explicit
profiles. Caller 1.9.39 measures the complete-unit quotation limit in UTF-8 bytes.
ProjectCommand 1.0.7 retains the first collected hash for each original path and
checks every collected original again before assembly. Its output explicitly
labels observed Git HEAD separately from collected working-file bytes. These
checks detect the reproduced source-change cases; they are not an atomic source
snapshot, a clean-tree assertion or a filesystem lock against all later writes.
See `complete-unit-byte-limit.json` and `project-source-consistency.json`.

Go producer 1.6.1 can record two or three ordered if/return guards followed by an
explicit return in the existing optional profile. Physical positions are checked
without interpreting `//line` directives as citation coordinates. Its three
packaged targets reproduced byte for byte with fresh compiler caches at the
recorded canonical source path. This is reproducibility of this compiler/source
cut, not native Windows validation or type/import resolution. The JavaScript
producer's optional ordered-guard child packet similarly preserves source
expressions; the ordinary Ruby writer does not consume that new child packet.
No implicit tool selection or retrieval route was added.

The actual twelve-pass self-documentation experiment completed in 1523.449
seconds. Nine section outputs passed the writer, three were refused, and full
review of forty bilingual fact pairs approved no complete response. Errors
included claiming an atomic-snapshot guarantee, treating a temporary evaluation
lifecycle as automatic deletion, assigning checksum checks to the metadata loader
and describing a client response bound as a property of Ruby. The corrected
chapter is a separate Codex-authored candidate. See
`agent-self-documentation-review.json` and
`chapters/documentation-agent-contracts/`.

A private RubyVM prototype attached exact lexical-method metadata to existing
range cards. Nine controls / 38 assertions passed on Linux MRI 3.4.11 and Darwin
MRI 2.6.10, without executing inspected source. Three new requests compared the
agent's own code and installed Rails actionpack 8.1.4; the original self-documentation
baseline was reused. A wrong method assignment improved in one arm, but the
return-shape error persisted and the Rails arm transferred another method's body
to the newly named method. The candidate was rejected for integration. Accurate
structural metadata is not proof that a model will use the right body or preserve
other facts. No live card preparation changed for this experiment. See
`ruby-lexical-owner-experiment.json`.

Python source-fact profile v4 adds a bounded local-initializer / while-true /
yield-await / named-except-break shape. It explicitly records syntax without
claiming exception-name bindings, AnyIO semantics or successful execution. The
actual Starlette case changed from safe unsupported refusal to a deterministic
draft followed by no-op; all output bytes and mtimes were preserved on rerun.
The two prior shapes retain byte-identical EN/PT paragraphs. Full checks passed
254 Ruby tests / 1704 assertions and 46 Python controls on both host and Linux.
Only one actual repository family supports this addition; no independent real
repository transfer is claimed. See `python-guarded-iteration-integration.json`.

The latest private diagnostic chain contains 142 complete response pairs / 284
language rows, including historical records. Eleven corrected chapter pairs /
22 language rows remain a separate candidate chain. All related languages,
prompt/metadata variants and repository families remain together. None of these
records is automatically consumed by the ordinary model context or a trainer;
there are still zero approved gold rows, training runs or intact independent
reserved holdout families claimed after the explicit Axum incident. These dated
supplements supersede current-state counts, not the historical evidence above.

### Additional module-boundary evidence

The follow-up metadata study parsed 34 frozen `go.mod` declarations and one
`go.work` across five repositories with the already recovered Go compiler.
`go mod edit -json` / `go work edit -json` used explicit inputs and no editing
flags; all metadata hashes remained unchanged. No packages were built or run and
no modules were downloaded. The SDK contributes 24 module declarations; the
Prometheus workspace names five module directories. Examples include a Chi
module named `rest-example`, a Prometheus module named `compliance`, the SDK's
nested OpenTelemetry module with three local replacements and the previously
observed Go Image Optimizer backend module. These are concrete reasons to reject
repository-root or remote-URL-only ownership inference.

`go-module-boundaries.json` records the full declaration inventory and five
source-path checks. It is diagnosis and a future resolver's acceptance criteria,
not an implemented import resolver. Any future resolver must explicitly freeze
workspace activation and local-replacement targets, respect module boundaries
and refuse out-of-scope or ambiguous paths. Parsing these declarations does not
establish package members, aliases, build constraints or runtime bindings. All
SDK submodules stay in the same conservative dataset family.

### Explicit coverage-policy integration

Caller 1.9.40 / project workflow 1.0.8 optionally accepts
`require_selected_evidence_coverage: true`. It rejects missing selected IDs,
duplicate-only substitutes and impossible fact budgets, and binds this policy to
request/cache/fingerprint metadata. Default/false request bodies stayed byte
identical in three real source cases. Two historical missing-card responses from
two development repositories were refused without altering prior owned outputs
or manifests; a known false all-ID response still passed. This is a bounded
coverage gate, not factual validation, automatic dependency discovery or a new
model-controlled tool route. Full Ruby checks passed 262 tests / 1787 assertions.
See `selected-evidence-coverage-integration.json`. The twelve-pass corrected
self-documentation chapter retains its explicitly frozen older source cut.

### Source families, activation and current candidates

A private predeclared-name census passed fifteen owned controls but refused an
actual SDK conclusion. The conservative imported-source union included the Go
`time` generator `genzabbrs.go`, whose build tag is `ignore` and package is `main`.
The study did not apply build constraints and retained that refusal. No builtin
binding, runtime semantics or production name resolver was promoted. See
`go-predeclared-binding-study.json`. This is another reason to separate a module
registry, package file selection, lexical names and runtime behavior.

The existing seventeen source-syntax targets retained exact EN/PT paragraphs and
physical quotations under current producers on host and Linux. Four new source
contracts matched previously verified real writer deliveries, producing a separate
21-pair / 42-row candidate cut with current provenance. Its two broad components
are development-exposed, and no trainer or ordinary model-context consumer loads
it. Fourteen corrected chapter pairs are a different artifact class. See
`source-syntax-candidate-reconciliation.json` and `dataset-curation.json`.

Five old Axum candidate queue rows now carry explicit current-campaign exclusions
instead of remaining selectable as unused transfer candidates. Historical reserve
and incident records remain intact. This reconciles the durable scheduler with
the dataset restriction; it does not recover an unseen holdout. Training remains
blocked at all-nine-gates readiness, with zero fully passed gates or approved rows.

## Latest source-boundary and restart evidence

The actual power interruption now supplies a concrete ambiguous-request incident,
recorded in `power-restart-analysis.md`: an audit event before transport does not
prove server receipt or completion. The proposed durable request states remain a
proposal, not an implemented exactly-once transport or new Harness. Existing
output journals and independently verified archives solve different recovery
problems from inference reconciliation.

The Redis follow-up uses only the existing application-selected profiles. A
complete cross-file helper exceeded the explicit-line-range profile's 1,900-byte
quote cap. The refusal was retained. A separately frozen experiment used the
already existing C definition-layout selector and its 6,144-byte unit cap; all
2,357 helper bytes and comments were preserved. No limit, extractor, automatic
retrieval, tool router, MCP implementation or plugin loader was added. The result
is in `redis-complete-helper-unit-study.json`: three selected IDs were cited, but
the complete response still failed ownership/propagation/branch review and the
writer refused it. This does not execute the proposed model-driven retrieval
experiment or establish its security/evaluation cases as passed.

The optional all-ID policy remains a coverage boundary. All six actual responses
using that policy cited their selected IDs, yet no whole documentary response was
approved. The current outcome matrix covers 54 documentary responses; it is a
selected development set and provides no global accuracy estimate. Explicit
source retrieval, syntax coverage, writer acceptance, bilingual equivalence and
factual approval must remain separate observations.

Current source/candidate/recovery totals and framework probes are dated in
`unified-candidate-lineage-v6.json`, `chapter-citation-integrity-v2.json`,
`current-aggregate-recovery.json`, `chunk-recovery-after-restart.json` and
`post-restart-framework-readiness.json`. The queue preflight groups 53 pending rows
into 24 contracts, retaining their non-ready status. A global cache/recovery
scenario may carry an upstream example contract; that metadata is not permission
to execute a redundant upstream generation. Independent holdout and training
approval remain absent. These supplements supersede the older count paragraphs,
without changing the architecture/implementation decision boundary.
