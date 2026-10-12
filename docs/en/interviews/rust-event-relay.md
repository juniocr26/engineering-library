# Rust Event Relay technical interview study guide

[English](rust-event-relay.md) | [Português brasileiro](../../pt-BR/interviews/rust-event-relay.md)

This portfolio studies reliable event delivery under failure. Current facts come from the [README](../../../../rust-event-relay/README.md), [architecture](../../../../rust-event-relay/docs/en/architecture/overview.md), [ownership milestone](../../../../rust-event-relay/docs/en/architecture/milestone-2-3.md) and source. First-person answers describe implementation, not production experience. Alternatives are learning comparisons; ADR 007 separately records the selected ownership decision. The 2026-10-10 audit executed no runtime checks. This 2026-10-12 update uses the separately recorded Milestone 2.3 validation; see the [current dossier](../architecture/rust-event-relay.md).

## 1 Overview and current scope

**Question: Is this already a delivery engine?**

**Model answer:** “The HTTP binary currently loads configuration/tracing and serves liveness with graceful shutdown. Separate modules provide an event envelope, PostgreSQL pending-event reader, confirmed RabbitMQ publisher and ownership models/contracts/schema and production PostgreSQL mutations. No worker connects acquisition, publication and completion yet. Reliable end-to-end delivery, retries and dead-letter handling remain future work.”

Milestones 2.1 publisher, 2.2 ownership types/ports/migration and 2.3 PostgreSQL operations are implemented. 2.4 orchestration, 2.5 worker/composition and 2.6 crash experiments are deferred. Study documents do not change those progress markers.

## 2 Architecture and execution paths

`main.rs` → config/telemetry → TCP listener → `application::serve`. `/health` returns `ok\n`; it does not connect to PostgreSQL/RabbitMQ or prove readiness. Shutdown uses SIGINT/SIGTERM on Unix. Injected shutdown futures let lifecycle tests use an ephemeral socket without global signal manipulation.

Separate data path: an injected `PgPool` backs `PostgresOutboxRepository::read_eligible`; it executes a bounded parameterized SELECT, restores validated envelopes and returns snapshots. `RabbitMqPublisher` implements the application-owned `EventPublisher`, owns a connection/channel, declares durable topology and publishes persistent JSON with stable event ID and confirms. Neither adapter is called by the HTTP binary.

[Persistence contracts](../../../../rust-event-relay/src/persistence/ownership.rs) expose native Send futures with static dispatch. SQLx/Lapin types stay in infrastructure; domain types validate invariants. Small contracts make responsibilities/test seams explicit, with generics/static dispatch rather than a runtime plugin registry. A boxed/dynamic contract could enable runtime adapter selection at allocation/dispatch cost; it has not been implemented here.

## 3 Event identity and transactional outbox

**Question: What must be atomic?**

**Model answer:** “The future producer must insert its business change and outbox event in the same local database transaction. The relay schema and reader exist, but no producer endpoint implements that transaction here. A remote broker remains outside the database transaction.”

The envelope preserves UUID v7 identity, UTC occurrence time, version, aggregate identifiers, optional correlation/causation IDs and JSON payload. Restoration validates data without inventing a new event ID. UUID ordering is not business delivery order; schema_version is not an automatic compatibility framework. Flexible JSON/aggregate strings cost compile-time payload/format guarantees.

**Follow-up:** Would a duplicate primary key prove an identical logical operation? No: it proves identity exists, not matching payload/business effects. Producer idempotency/reconciliation is still a design responsibility.

## 4 Snapshot versus ownership

**Question: Can two workers read the same pending event?**

**Model answer:** “Yes. The existing reader selects pending rows by caller cutoff and count without claiming or locking rows for delivery. It also includes leased and attempt-exhausted pending rows. A snapshot is data, not permission to publish or complete.”

The query orders availability, creation and ID. Count bounds rows, not payload bytes or concurrency. Invalid selected data fails the entire batch; no silent repair/quarantine or retry exists. Pool lifecycle/timeouts are caller responsibilities. Domain row restoration and checked private timestamp/JSON decoding reject unsupported stored values and preserve JSON numeric precision.

## 5 Durable leases and database authority

**Question: Why a durable lease instead of holding a transaction while publishing?**

**Model answer:** “ADR 007 chooses short acquisition/completion transactions with publication outside them. Holding row locks and connections during broker waits costs resources and still cannot undo broker acceptance if the database transaction rolls back. Durable expiry supports recovery, at the cost of token/time predicates and possible overlapping external sends.”

Implemented pure rules keep leased events pending, increment acquisitions, replace expired authority with a fresh token and reject stale owners at the exact expiry boundary. Completion clears the lease and sets processed; release clears ownership without selecting a retry schedule. Event ID stays stable; ownership token identifies one acquisition. `attempt_count` models committed acquisitions, including crashes before sending, not actual network sends.

The ports require database time sampled after lock acquisition and known committed acquisition before returning owned data. **Milestone 2.3 implements these ports in a separate infrastructure ownership module; the reader remains observation only.** The 2.2 migration adds coherent nullable lease fields; constraints prove row shape, not legal transition history or uniqueness of every historical token. `CommitUncertain` means a mutation may have committed; `OwnershipLost` is an ordinary unmatched-authority result. Neither should become assumed success.

**Follow-up:** Does a token fence RabbitMQ? No. A stale process may still send; database authority only guards later database transitions. Consumer idempotency remains necessary for future duplicate-tolerant effects.

## 6 Broker confirmation and failure windows

| Scenario | Current behavior / limitation |
| --- | --- |
| Serialization or disconnected adapter | Classified publish error; no successful acceptance |
| Mandatory publish cannot route | Returned message classified Unroutable |
| Negative confirmation | Rejected |
| Timeout/error/cancellation after send begins | Acceptance may be uncertain; channel retired |
| Broker Ack without return | Publisher success; not proof of consumer processing |
| Success followed by future completion failure | Potential duplicate on recovery; orchestration is absent |

Publication is serialized to one in-flight call with a mutex and bounded waits. The mutex wait and send/confirm each have their own timeout, not one total deadline. Connection setup and close also have bounded waits. The adapter does not automatically reconnect/retry. Definite rejected/unroutable outcomes need not retire the channel; uncertain outcomes do. Persistence/publication errors format sanitized categories while retaining typed sources, so exposing source chains requires a deliberate diagnostic policy.

**Model answer:** “I distinguish unavailable before send, known broker rejection and uncertain acceptance. I would not mark an event processed on any publish error. Broker acceptance followed by uncertain database completion is the future duplicate window; no exactly-once claim follows from confirms or leases.”

## 7 Testing strategy and evidence

Default tests exercise envelope restoration, invariants, ownership boundaries, contract futures, mapping errors, HTTP lifecycle and publisher confirmation/configuration behavior. Some database-independent publisher tests use local TCP sockets; independent means no live PostgreSQL/RabbitMQ, not zero I/O.

Opt-in PostgreSQL tests own isolated generated databases and verify reads, original migrations and the ownership up/down migration. Real RabbitMQ tests cover routing/confirm and timeout/cancellation uncertainty. The checked-in CI has default, PostgreSQL and RabbitMQ jobs, but workflow presence is not evidence of a successful remote run. [Historical validation](../../../../rust-event-relay/docs/en/testing/validation-results.md) records prior executions; none were repeated here. Milestone 2.3 adds 12 real PostgreSQL ownership cases, including disjoint concurrent claims, held-row skipping and post-lock expiry rejection; pure/fake tests alone establish none of those guarantees. An isolated proxy also tests lost acknowledgement after observed server COMMIT; cancellation during COMMIT remains unverified.

## 8 Alternatives and interview follow-ups

| Choice | Benefit | Cost / reasonable alternative |
| --- | --- | --- |
| Producer-owned local outbox | Atomic business/event intent | Needs future producer integration; CDC could change capture boundary |
| Short transactions and durable leases | Avoids locks during remote waits | Stale external sends; long row lock still cannot prevent duplicate remote effects |
| Explicit reader/publisher/ownership contracts | Separate observation, authority and transport | More boundary types; one combined adapter would hide distinct semantics |
| RabbitMQ confirms and mandatory routing | Detects broker acceptance/unroutable messages | No consumer-effect guarantee; HTTP/webhook adapter has different acknowledgement semantics |
| Incremental HTTP scaffold | Testable lifecycle/operations | Liveness is not a functioning relay |

Practice: What happens at exact expiry? Why sample time after lock waits? Why can an empty acquisition still leave backlog? What does release do to available_at? Why is CommitUncertain different from rollback? How can consumer deduplication and business effects share one transaction? Which tests must precede a production claim?

## 9 Ordered study roadmap

1. Trace HTTP/configuration and learn the distinction between liveness and readiness.
2. Restore an envelope and explain identity, occurrence time and payload validation.
3. Trace outbox schema/reader, count limits, malformed-row behavior and producer transaction boundary.
4. Explain broker confirms, mandatory routing and uncertain acceptance.
5. Trace pure lease boundaries and ports; read ADR 007 before comparing ownership alternatives.
6. Review tests/CI and historical evidence; separate models/schema, verified mutations and absent orchestration.
7. Study 2.4–2.6 prerequisites and duplicate/idempotency failure windows without marking them delivered or studied.

## Additional source-grounded interview deep dives

Original questions and answers above are preserved. IDs below identify this additional sequence; they do not renumber the retained material. Levels guide rehearsal, not implementation status. Follow-ups include answers so this sequence is self-contained.

### Q001 — Introductory: What actually runs when the relay binary starts?

**Answer:** Implemented: main loads config, initializes JSON tracing, binds TCP and calls the Axum HTTP lifecycle. GET /health returns fixed ok; SIGINT/SIGTERM request graceful shutdown on Unix. The binary does not create the PostgreSQL pool, connect a RabbitMQ publisher or start a polling worker. Separately callable modules restore envelopes, read eligible snapshots, publish with confirms and model ownership contracts. Separating modules enables focused tests, but module presence is not proof they form a delivery pipeline.

Follow-up: Why can health be green while the broker is unavailable? It does not call the broker or database; Compose service health is a separate startup gate. Follow-up: What would readiness require? Define whether accepting work depends on reachable stores, topology, active worker and backlog capacity, then compose checks with bounded failure behavior. That is hypothetical, not a metrics/readiness feature currently delivered. Rust memory safety helps within language boundaries but does not make distributed delivery correct or eliminate logic/transport uncertainty. Explain current scope before proposing reliability improvements.

### Q002 — Intermediate: How do event identity and JSON precision survive persistence?

**Answer:** Implemented: new envelopes generate UUID v7 and UTC time; restoration preserves stored identity, occurrence time, aggregate strings, nonzero version, optional correlation/causation UUIDs and JSON payload. Schema version is a number, not a registered payload evolution engine. PostgreSQL JSONB preserves semantic JSON rather than original formatting/key order. The adapter uses private JSONB decoding with version-byte checks and serde_json arbitrary_precision to avoid rounding large integers/decimals. Checked timestamp decoding rejects infinity/out-of-range values instead of unchecked arithmetic. Unsupported selected data makes the whole read fail.

Follow-up: Does UUID v7 impose global business order? No. Creation timestamps/IDs support sorting, but causality and aggregate order require a separate contract. Follow-up: Why not silently repair malformed stored events? That could invent identity or meaning and hide producer corruption. Quarantine is a possible future policy but absent. A typed domain payload could give stronger compile-time guarantees at tighter producer/consumer coupling; the current relay intentionally handles a generic envelope. Validate business compatibility separately; storage restoration alone does not validate every payload schema.

### Q003 — Challenging: Why is a bounded eligible snapshot not permission to deliver?

**Answer:** Implemented: the PostgreSQL reader selects pending rows with available_at <= cutoff, orders availability/creation/ID and uses a checked LIMIT. It does not use an ownership predicate, claim rows or mutate them, so two readers can observe the same event, including leased or attempt-exhausted pending rows. fetch_all bounds row count but not total payload bytes. Snapshot isolation determines what was visible at the query; metadata can become stale immediately. This is an observation contract, not delivery authority.

Follow-up: Could an empty batch mean there is no backlog? It could mean no rows meet that cutoff; future-due, processed or excluded rows are another set. An empty acquisition can also mean active leases/exhausted attempts, so it does not prove empty backlog. Follow-up: What about one malformed selected row? Restoration collects Result values; any invalid selected row fails the batch without returning partial results or repairing storage. This can repeatedly block useful rows. A skip/quarantine policy needs explicit loss/diagnostic semantics and tests; it is not implemented. Broadening a reader into generic CRUD would obscure these distinct guarantees.

### Q004 — Challenging: What guarantees are selected by leases and which are still only contracts?

**Answer:** Implemented: ADR 007 records short database transactions and publication outside locks. Pure delivery rules use event identity plus acquisition token, reject stale/expired authority and clear coherent ownership on completion/release. Expiry is exclusive: at exact expires_at the owner no longer has authority. Attempts count committed acquisitions, not actual sends. The migration enforces coherent nullable fields on pending rows; ports describe acquisition/completion/release and CommitUncertain. The production PostgreSQL adapter now implements these mutation ports with short Read Committed transactions and no hidden retries.

Follow-up: Why sample database time after obtaining a lock? Waiting can make an earlier sampled time falsely treat an expired lease as active. The 2.3 integration test coordinates an actual row-lock wait spanning expiry and rejects both completion and release afterward. Exact equality is still deterministic model evidence. Follow-up: Does the token fence RabbitMQ? No. It guards future database predicates; a stale process can still send externally. Long transactions would hold locks/connections across remote waits and still could not undo an accepted send on rollback. Leases trade those costs for expiry/recovery complexity and possible duplicate publication. Consumer deduplication remains necessary in a future pipeline; pure tests cannot prove database concurrency behavior.

### Q005 — Challenging: How do confirms, returns, timeouts and completion create different failure windows?

**Answer:** Implemented: the publisher sends persistent JSON on a durable bound topology with mandatory routing and confirms. Ack without return is success at the broker boundary; returned mandatory messages are unroutable, nack is rejected, and timeout/error/cancellation after sending may be uncertain. The adapter serializes one in-flight call and retires the channel on uncertain outcomes; it does not reconnect or retry automatically. A confirm is not a consumer acknowledgement or business-effect commit.

Follow-up: What if a future worker gets Ack and then cannot confirm database completion? Publication may have succeeded while the row remains eligible for recovery, so duplication is possible. Conversely, marking processed before publication risks loss. Follow-up: How would a consumer make duplicate effects safe? Hypothetically record stable event ID and apply the business effect in one local transaction with a unique deduplication key. External secondary effects still need their own outbox or equivalent coordination. None of that consumer/worker exists here. Exactly-once claims cannot follow from one broker Ack, a mutex or a lease token.

### Q006 — Intermediate: How do static dispatch, isolated tests and operational limits fit together?

**Answer:** Implemented: ports return native Send futures and keep SQLx/Lapin protocol types in infrastructure. This supports generic/static-dispatch callers and fakes without mandatory boxed futures. Dynamic dispatch could support runtime-selected adapters but needs an object-compatible interface and often allocation; that is an alternative rather than the current API. Default tests exercise invariants/contract mapping and real local HTTP sockets; opt-in PostgreSQL cases own exact generated databases and broker cases exercise routing/uncertainty. Pure ownership tests do not establish concurrent SQL claims; the separate 2.3 integration suite now demonstrates them under tested conditions.

Follow-up: Is workflow configuration proof of CI success? No. Historical executions are separate records, and the 2026-10-10 audit ran no runtime checks; 2.3 validation is recorded separately. Follow-up: What remains before production? Worker orchestration/composition, retry/quarantine policy, consumer-effect evidence, bounded payload/admission limits, telemetry, TLS and recovery tests. The current publisher admits one in-flight send with separate gate/publish deadlines; row limits do not bound bytes. Supervisor shutdown budgets and persistent volumes are development mechanisms, not verified power-loss durability, production capacity or backup recovery. No benchmark chart is justified by those settings.


### Q007 — Challenging: What does uncertain COMMIT require from the next use case?

**Answer:** Acquisition returns owned data only after acknowledged commit; an uncertain commit returns an error even though a lease/count may already be durable. Completion or release may likewise have committed before acknowledgement disappears. Ordinary server rejection differs: the real deferred-constraint fixture proves rollback and OperationFailed. Transport/protocol loss at commit conservatively maps to CommitUncertain; ownership mismatch remains OwnershipLost. These classifications preserve separate responsibilities rather than silently retrying or treating a conflict as previous success.

Follow-up: Should the caller publish after uncertain acquisition? No ordinary confirmed claim is available. Inspect durable lease state operationally or allow expiry and use a fresh acquisition request; preserve event identity. Follow-up: What if completion is uncertain? Processed may already be durable; blind repetition or republishing can misinterpret the state or duplicate publication. The use case must surface uncertainty and define reconciliation, while tokens still cannot fence RabbitMQ. Follow-up: Does cancelling the future prove rollback? No. SQLx queues rollback for an open dropped transaction but commit can already have occurred, and cancellation may return no classified error. Tests cover blocked pre-mutation cancellation and error mapping, and an isolated lost-acknowledgement proxy for all three operations; cancellation during COMMIT remains unverified. The proxy loses the response after observing server completion and inspects durable state independently, demonstrating one committed uncertain outcome without generalizing it to all uncertainty.
