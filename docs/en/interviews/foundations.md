# Cross-cutting foundations interview

## Current engineering update — Milestone 2.5, 2026-10-12

The [separate Rust worker](../../../../rust-event-relay/docs/en/architecture/milestone-2-5.md) composes validated configuration, JSON tracing, a dedicated PostgreSQL pool/repository and RabbitMQ lifecycle. [Application scheduling](../../../../rust-event-relay/src/application/worker.rs) uses static dispatch and controlled dependencies; [composition](../../../../rust-event-relay/src/bin/relay.rs) constructs concrete infrastructure. It admits one delivery at a time, creates no worker tasks and obtains a fresh acquisition token per invocation. NoEvent paces one invocation, without proving an empty backlog. Confirmed acceptance plus Applied completion alone permits immediate next admission.

General lesson: pacing between invocations controls operational pressure; it does not write a durable retry schedule. Rust uses 1000 ms idle/failure waits and 5000 ms reconnect waits by default, preserving available_at/last_error/attempt semantics. Invalid or permanently failing eligible rows can still obstruct progress. Fairness, backoff/jitter, quarantine and DLQ need separate policies and evidence.

General lesson: a unusable connection is a lifecycle fact, not a reason to replay a prior effect. Rust closes/replaces after Unavailable/Uncertain or a known retired/disconnected channel and acquires nothing while knowingly lacking a usable publisher. Serialization/Unroutable/Rejected keep a usable connection. Reconnection does not reconcile previous broker acceptance. Unknown acquisition has no confirmed claim; unknown completion may conceal processed state. No compensation or previous-claim republication is introduced.

Concrete Rust pattern (abridged from the worker; meaningful types belong to existing ports):

```rust
let request = AcquireRequest::new(config.lease); // fresh ownership token
let outcome = deliver_once(repository, publisher, request).await;
let action = decision(&outcome); // inspect completion and publication separately
// Continue, Idle, Pace or Replace; waits must race the shutdown signal.
```

General lesson: shutdown is one finite resource budget. Stop admission first, allow current work to drain, cancel only when its drain expires, then close publisher and pool using the same absolute deadline. Dropping a future can suppress the outcome after committed/accepted effects; blindly releasing an abandoned claim is unsafe. Rust defaults to 15 s drain within 25 s total, Supervisor 30 s per child and Compose 65 s for sequential groups. Pool acquisition timeout does not bound queries: dedicated session statement/lock defaults are 5 s/3 s, distinct from RabbitMQ network waits and the 60 s durable lease. These durations cannot guarantee that the lease remains live.

[Controlled tests](../../../../rust-event-relay/tests/worker.rs) prove scheduling/lifecycle policy; [isolated real composition](../../../../rust-event-relay/tests/worker_smoke.rs) verifies delivery/completion and Supervisor named/collective operation. Happy-path evidence is not crash/recovery evidence. Shared ownership migration remains pending, relay autostart is false and /health proves HTTP liveness only. Configuration/setup failures terminate with sanitized diagnostics; RabbitMQ runtime outages reconnect explicitly. Only the app image/container was updated, preserving shared infrastructure/state.

Transferable reference for future Viva Bem improvements: bound admission, keep infrastructure construction outside scheduling, separate external acceptance from durable completion, preserve uncertainty and primary/cleanup errors, and plan finite cleanup. This is a future engineering reference; no claim is made that Viva Bem uses this architecture, and no private implementation is described or modified. An optional graphical interface belongs after core completion if a concrete operational need exists. Next Rust scope: 2.6 integrated crash/failure/recovery experiments and milestone closure, with no throughput/fairness/consumer-effect or end-to-end at-least-once claim.

Earlier dated sections retain historical scope and are superseded on worker status by this update.


## Application orchestration and uncertain effects — 2026-10-12

General principle: an application use case sequences focused ports while adapters own protocols and transactions. Confirmation before local completion separates external acceptance from durable local acknowledgement and consumer effects. Preserve primary and cleanup failures independently; cancellation and unknown acknowledgements may hide effects rather than prove rollback. Leases permit recovery but do not fence an external destination. The [Rust 2.4 dossier](../architecture/rust-event-relay.md) explains the concrete choice to release definitive failures once and retain uncertain leases. These choices are project policy, not universal retry rules.


These conceptual comparisons do not imply runtime integration. Implemented facts, general theory and hypothetical alternatives are explicitly separated.

### Q001 — Intermediate: How do atomicity, durability and idempotence differ across these projects?

**Answer:** Theory: atomicity concerns all-or-nothing visibility within a specified boundary; durability concerns survival after acknowledged state under defined failures; idempotence concerns repeated effects. They are independent. ENV Auditor replaces one target atomically but does not transact across targets or fsync the directory; a stable plan can be semantically wrong. Redis INCR atomically allocates an ID but cannot atomically commit Cassandra mapping. Rust's future producer must couple business change/outbox in one local transaction, while broker acceptance remains external; its worker is absent. These are different boundaries, not contradictory claims.

Follow-up: Can retry after timeout be safe? Only with knowledge of possible effects and an idempotency/reconciliation contract. A Cassandra write may exist after a lost response; a RabbitMQ publish may be accepted after a confirm timeout. Treating timeout as rollback can duplicate effects. Follow-up: Does volume persistence prove durability/backup? No. Storage survives ordinary recreation but may fail with the host or propagate corruption; backups need independent recovery evidence. Hypothetical recovery designs must name the boundary and failure model rather than say “reliable” without qualification.

### Q002 — Intermediate: What does a layered architecture actually protect?

**Answer:** Theory: a boundary localizes responsibilities and representations; its value depends on actual dependency direction and behavior. Go separates HTTP, context/input validation and codec work using small interfaces. URL Shortener separates routes/controllers/service/adapters but its service imports concrete adapter types, so interfaces cannot be assumed. Payment Lab maps JPA entities to DTOs inside a transaction, while its service imports a concrete repository. Rust keeps SQLx/Lapin in infrastructure and defines focused read/publish/authority contracts. None requires empty layers merely to claim a pattern.

Follow-up: Are DTOs a security boundary? They can prevent accidental field exposure but do not replace authorization, value validation or log handling. Follow-up: When add a port? When a stable application requirement should not depend on protocol details or when meaningful tests/alternate adapters need it. More abstraction adds types/mapping and can hide important consistency semantics. Compare concrete costs: a generic CRUD interface would obscure Rust's snapshot versus authority distinction; a focused contract makes that distinction reviewable. These comparisons are conceptual; the projects do not call each other's layers.

### Q003 — Challenging: How do you estimate performance without inventing benchmark results?

**Answer:** Theory: count work and resource growth, then label the estimate as analysis. ENV Auditor scans entries, sorts per directory and processes literal blocks; its list-membership append path can become quadratic in many missing keys. Go's decoded work grows with pixels/frames, and native allocations plus buffered proxy results dominate beyond encoded-byte size. URL Shortener includes synchronous network calls and a serialized counter; Payment Lab materializes all visible entities/DTOs; Rust materializes a bounded batch by rows and serializes publisher admission. These mechanisms suggest measurement targets, not operations per second, production capacity or comparative language superiority.

Follow-up: What would a useful benchmark need? Representative input distributions, dependency versions/topology, hardware, concurrency, warmup, method, units and uncertainty, plus separate latency/throughput/peak-memory and correctness observations. No benchmark is authorized in this task. Follow-up: Why can Big-O be insufficient? Native codec settings, payload sizes, network tails and simultaneous allocations can dominate constants. A 32-million-pixel bound gives a rough RGBA byte estimate but does not certify total RSS. Do not turn constraints, test counts or Docker replicas into performance charts.

### Q004 — Introductory: Which security mechanisms solve different problems?

**Answer:** Theory: validation checks representation or invariants, authentication checks identity/provenance, authorization permits actions, encryption protects confidentiality and integrity mechanisms detect unauthorized changes. URL syntax is not abuse prevention; Basic is credential authentication and needs protected transport; affine Base62 obfuscation is not encryption. CORS controls browser access behavior and does not authorize non-browser requests. Payment Lab deny-all outside allowlisted GETs protects the current surface, not a future payment workflow. Rust's lease token guards future database authority, not broker sends or payload secrecy. ENV Auditor private plaintext backups and Go pixel checks reduce particular risks without sandboxing hostile processes.

Follow-up: Do sanitized responses imply sanitized logs? No. Payment Lab logs exceptions; Rust retains typed sources; output key/path identifiers also reveal metadata. Follow-up: How would future signed webhooks differ from TLS? TLS protects a connection; provider signatures authenticate a specified payload under a specific key/protocol, with replay and raw-body requirements. No Stripe webhook is implemented here. Discuss hypothetical controls as new requirements, and verify their source contracts before implementing them; do not infer cryptographic guarantees from a hash function appearing in code.

### Q005 — Intermediate: How do fakes, integration tests and liveness limit what you can claim?

**Answer:** Theory: evidence proves the assertions at the exercised boundary under its fixture conditions. Fakes can prove service ordering/error translation while excluding real stores, locks or native codecs. Real PostgreSQL tests can verify constraints and selected schedules in isolated databases but not every crash or power loss. A historical test result belongs to its recorded tree/environment; source inventory and CI workflow existence do not mean new passing execution. Go browser behavior and native-library races require different evidence from unit tests. Rust's pure lease tests do not demonstrate absent mutation SQL.

Follow-up: Is a green health response readiness? Not by itself. Rust's fixed health checks process liveness; Shortener's OpenAPI probe checks serving; Payment Lab readiness includes database connectivity but no reconciliation/provider flow. Follow-up: How choose the next test? Start from a material invariant and inject the failure at its boundary: backup-before-replace, uncertain remote write, stale owner after lock wait or transaction-scoped DTO mapping. Add tests that can fail for the requirement rather than merely restating implementation. Application tests were not executed in this documentation-only review.

### Q006 — Challenging: How do deployment, rollback and recovery differ for stateless and stateful components?

**Answer:** Theory: code rollback switches artifacts; recovery restores a valid operational/data state. Go has ephemeral processing and native runtime dependencies, so compatible old builds matter without an upload database. ENV Auditor writes real files and backups, so recovery may require restoring exact originals while preserving later edits. Shortener must coordinate Redis ID state, Cassandra mappings and obfuscation settings. Payment Lab must preserve Flyway history and initialized volume identity. Rust must preserve events/migrations/broker data and still implement the absent worker path before claiming recovery delivery.

Follow-up: Is a migration down an undo? It may remove schema/data rather than recover original business state. Reapplying schema does not restore rows. Follow-up: What should a reviewable production procedure specify? Artifact/schema compatibility, backup identity, tested restore, failure triggers, safe forward-fix/rollback and bounded observable checks. Current local Compose reload/caches/health are development facts; no production TLS/HA rollout, restore exercise or measured RTO/RPO is verified. Naming a project or volume is not a data migration. These comparisons are independent projects, not a shared production platform.



## Cross-system recovery evidence

Transport confirmation, SQL durability and business effects are separate facts. A crash between accept and completion can repeat an ID; lost SQL acknowledgement can hide an already durable processed state. SQL tokens do not fence external systems. Use the [Rust follow-ups](rust-event-relay.md) to explain finite-schedule limits, actual expiration and reconciliation without blind compensation.
