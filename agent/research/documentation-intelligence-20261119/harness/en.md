# Bounded documentation Harness: current architecture and interoperability

This source-grounded research cut is separate from production integration.
The current Ruby core remains at owner HEAD45c3cd0; new optional APIs are executed
only in research/tests. The study PDF was not found in the checked local scopes
or two current metadata-only Drive searches; [scope receipt](../pdf-plan-access-current.json)
does not claim absence everywhere.

## Existing flow and responsibility

The ordinary model arm is application-directed: owner configuration selects source;
Command.process checks ownership and prepares evidence, fixed skill context and
identity; exact no-op/reuse can avoid inference; otherwise call_model invokes
Ollama and validates the returned envelope. Paragraph/source checks and source
rechecks precede owned draft application. ProjectCommand coordinates declared
sections and assembly. These paths do not dispatch model-selected tool calls.

The research arm adds operator-frozen HelperRetrieval calls before one model
request. It supplies source quotations, not permission or verified helper semantics.
The two-arm adapter comparison did not improve model coverage. Registry/receipt
correctness and complete-contract EN/PT review remain separate gates.

| Capability | Status | Current finding | Source evidence |
|---|---|---|---|
| Application-directed orchestration | CONFIRMED | Command.process and ProjectCommand.process control selection, cache/inference, validation and owned output. No model-selected planner is inferred. | backend/lib/documentation/command.rb, backend/lib/documentation/project_command.rb |
| Model identity before/after inference | CONFIRMED | verify_model_identity checks the named model and active skill hashes against tags; call_model verifies complete envelopes. | backend/lib/documentation/command.rb |
| Model-selected tool dispatch in ordinary requests | ABSENT | source_model_request supplies messages/prompt, schema and options, without a tools dispatch loop. Research helper selection is operator-frozen. | backend/lib/documentation/command.rb |
| Optional helper API executed in research | CONFIRMED | Version0.1.2 has37 tests and9 actual-source cases. It is not wired into ordinary Ruby inference. | agent/tools/documentation_retrieval.py |
| Bounded exact source provenance | CONFIRMED | Registry, revisions, hashes, physical quotes and native-producer identity are checked in their explicit profiles. | agent/tools/documentation_retrieval.py, agent/tools/go_source_ast.py, backend/lib/documentation/go_ast_command.rb |
| Dependency/binding comprehension | PARTIAL | Closed facts and the optional build-filtered Go proof cover narrow cases. General imported helper semantics and runtime bindings remain unresolved. | agent/tools/documentation_lifecycle.py, agent/tools/documentation_retrieval.py |
| Three fixed instruction contexts | CONFIRMED | skill_context reads exactly evidence, authoring and review English context blocks in skills mode; baseline returns empty context. | backend/lib/documentation/command.rb, agent/skills/evidence/SKILL.md, agent/skills/authoring/SKILL.md, agent/skills/review/SKILL.md |
| Portable skill discovery/activation | PARTIAL | Current fixed files lack name/description YAML frontmatter. No metadata discovery/activation path was found in the inspected loader. | backend/lib/documentation/command.rb, agent/skills/evidence/SKILL.md, agent/skills/authoring/SKILL.md, agent/skills/review/SKILL.md |
| MCP in documentation runtime | ABSENT | Inspected paths use Ollama HTTP and verified subprocesses; no MCP dispatcher/server was added. Codex host connectors are a separate environment. | backend/lib/documentation/command.rb, agent/tools/documentation_retrieval.py |
| Agent Plugins conformance | NOT VERIFIED | No compatible package/client conformance test was run. A SKILL.md basename alone is not a conformant plugin package. | agent/skills/evidence/SKILL.md |
| Whole-job budgets | PARTIAL | Source and response limits are explicit; helper attempts/quote budgets are per instance. Persistent global tool budgets are not implemented. | backend/lib/documentation/command.rb, agent/tools/documentation_retrieval.py |
| Cancellation and deadlines | PARTIAL | Workers use3/20-second subprocess deadlines; transport uses request timeouts. End-to-end remote inference cancellation is not verified. | agent/tools/documentation_retrieval.py, backend/lib/documentation/command.rb |
| Journaled helper duplicate suppression | CONFIRMED | Requests/results/receipts are exclusive; missing receipt or legacy data never triggers automatic extraction retry. | agent/tools/documentation_retrieval.py |
| Ambiguous inference completion | PARTIAL | Raw requests/responses are retained. A disconnected inference may have completed remotely; no general server reconciliation proof exists. | backend/lib/documentation/command.rb |
| Tool and output permissions | PARTIAL | The optional API trusts operator-supplied read registries; source remains read-only while private audit records are written. No multi-user authorization service exists. | agent/tools/documentation_retrieval.py, agent/tools/documentation_maintenance.py |
| Retrieved instructions remain data | PARTIAL | Request allowlists and schemas restrict effects; source labels do not guarantee model compliance. A critical false REMOVE is preserved. | agent/tools/documentation_retrieval.py, backend/lib/documentation/command.rb |
| Human-content ownership boundary | CONFIRMED | Current caller ownership checks and isolated maintenance refuse unowned/stale writes; recommendations do not grant publication approval. | backend/lib/documentation/command.rb, agent/tools/documentation_maintenance.py |
| Local evidence and recovery | CONFIRMED | Independent code/model restoration and137 restored tests passed on Mac/Linux; remote loss and trainer-state recovery are unverified. | agent/recovery/bootstrap.py, agent/recovery/bundle.py |
| Automatic trainer or archive ingestion | ABSENT | No optimizer runs or automatic research-dataset loader are present in the inspected authoring path. Training gates remain closed. | backend/lib/documentation/command.rb |

## Standards and proposed boundaries

The consulted MCP revision is2026-07-28. Its core uses self-contained requests
and per-request capability information; connection-scoped assumptions from older
revisions cannot be copied blindly. [Core specification](https://modelcontextprotocol.io/specification/2026-07-28)

MCP defines tool input/output schema contracts and separate protocol/tool errors.
Annotations require trust; transport compatibility cannot authorize filesystem
access. Our future status mapping would be an application convention, not an
accuracy guarantee. [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

The transport binding carries metadata and frames messages. A future bridge must
bind authorized jobs independently of a connection; constructing a new internal
tool per request would reset its current per-instance budget. This is a design
inference from the current code and protocol. [Transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)

Cancellation differs by transport and can race completed work. A timeout must
not be treated as proof of rollback or permission to repeat an unknown inference.
[Cancellation](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation)

Agent Skills requires metadata in SKILL.md. The current three fixed contexts lack
that metadata; a filename is insufficient for conformance. Progressive discovery
is a distinct loader capability. [Format](https://agentskills.io/specification),
[client guidance](https://agentskills.io/client-implementation/adding-skills-support)

Agent Plugins1.0.0 standardizes a root plugin.json and optional fixed components.
Package containment does not sandbox its subprocess. A future reusable package
would need client/permission validation beyond wrapping these files.
[Specification](https://agent-plugins.org/specification)

## Compare three approaches to the same helper

| Dimension | Internal API | Local MCP exposure | Skill/plugin distribution |
|---|---|---|---|
| Factual potential | Exact missing source; measured quote quality | Same evidence behind another interface | Procedure alone cannot supply missing source |
| Provenance | Registered source/hash/selector and receipts | Preserve those checks plus wire identity | Preserve component provenance and underlying tool checks |
| Complexity | Already implemented in research | New client/server/version/process lifecycle | New compatible loader/package/permission review |
| Dependencies | Existing Python and packaged Go producer | Protocol implementation/runtime still unselected | Compatible client plus the underlying retrieval runtime |
| Security | Source read-only; own journal writes | Same source policy plus authorized job/transport control | Package trust plus runtime containment and tool policy |
| Interoperability | Private application API | Standardized boundary after conformance testing | Portable procedure/package after client testing |
| Latency/resources | Worker deadlines3/20s; no controlled latency win claimed | Not implemented or measured | Context/discovery cost not measured |
| Maintenance | Narrow source/receipt contracts | Protocol compatibility in addition | Client/package compatibility in addition |
| Current status | Executed in research, not ordinary routing | Proposed only | Proposed only |

They can complement one another: the same internal implementation could later
sit behind MCP and be distributed with a procedural skill. Packaging adds no
demonstrated factual improvement by itself.

## Risk-ranked next work and decisions

1. High: enforce complete source/binding evidence and preserve unknowns. The
   false REMOVE and failed helper explanation justify independent semantic checks.
2. High: bind current reference versions before scoring or curating data. The
   V1/V3 reconciliation is a real diagnostic, now covered by849 reference checks.
3. High: keep retrieved instructions outside permission authority. A model can
   still misread a comment even when the tool enforces read-only access.
4. Medium: add an operator-owned whole-job step/deadline ledger before autonomous
   routing. Existing helper limits are per instance, not a durable global budget.
5. Medium: reconcile unknown inference completion before any new attempt.
6. Deferred: approve a specific MCP SDK/version, transport, allowed roots, retained
   artifacts, permissions, cancellation/restart policy and conformance checks.
7. Deferred: approve plugin packaging/loading and any production prompt/tool route
   separately. No server installation or package is created by this note.

The [existing measured experiment](../owned-adapter-helper-comparison.json) and
[tool regression](../helper-cache-integrity-evaluation.json) answer different
questions: helper access is feasible and recoverable; better generated architecture
has not been demonstrated. Rollback means omitting the optional API call while
preserving journals; ordinary Ruby routing has not changed.

The Anthropic account motivates incremental durable handoffs; its Git-write
workflow is inapplicable under this owner's restrictions.
[Engineering account](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)
The OpenAI account motivates legible repository evidence and enforceable feedback;
its reported outcomes do not establish local model quality.
[Engineering account](https://openai.com/index/harness-engineering/)

Research completed: current map, capability matrix, primary-source comparison and
decision boundaries. Internal experiment executed; production MCP/plugin integration
not performed; neural training not performed.
