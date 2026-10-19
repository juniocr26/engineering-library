# rust-event-relay — Technical FAQ

[Project index](../index.md) · [Português brasileiro](../../pt-BR/faq/index.md)

Technical questions, detailed answers and follow-ups are available directly on this page. Historical milestone statements retain their dates; current corrections below take precedence. First-person examples describe portfolio artifacts, not employment experience. The [study guide](study-guide.md) retains its existing URLs and anchors for compatibility.

## Current source review — 2026-10-19

The answers below were checked against selected current source and test definitions. No sibling application tests or services were executed. See the [scope and evidence record](../operations/documentation-audit-2026-10-19.md).

### Q016 — Can one completed run accept multiple duplicate-publication actions?

**Answer:** Yes in the current tree. Migration `20261019000000_multiple_duplicate_actions.up.sql` removes the unique run constraint and adds a run/history index. The repository still reconciles action `request_id` before new admission: retrying the same identity returns its prior action, while changed run/copy intent conflicts. New identities can admit up to three retained actions for a run, subject to four queued/executing and 100 retained actions globally. Copies must be 1 or 3; three copies require the concurrent scenario. Eligibility also requires processed outbox and completed inventory receipt with stock 15. This is bounded local demonstration behavior, not arbitrary replay or broker administration. Multiple actions preserve the original event envelope; consumer deduplication, not action admission, prevents another stock increment.

### Q017 — Does an HTTP timeout prove the producer or action was rolled back?

**Answer:** No. The dedicated demo middleware returns a sanitized 503 after its eight-second timeout, but a transaction may already have committed. Reuse the same request identity and inspect/reconcile evidence rather than generating another command identity. The demo API separately checks a 64-character bearer token, optional matching localhost/loopback Origin and `x-demo-client: demo61`; its two-permit semaphore and ten requests per second are local admission bounds, not a distributed rate-limit guarantee. Dedicated composition validates the demo database fingerprint, uses two pool connections and separate SQL/lock/acquisition timeouts. Static test definitions include lost commit acknowledgement, cancellation after server commit, identity conflicts and history reads. They do not establish new execution, global crash safety or production rollout.


## Reading boundary — updated 2026-10-18


Use the [current dossier](../architecture/overview.md) and [final-scope questions](#final-local-scope-questions) for present behavior. Earlier questions/answers below preserve their milestone scope, including formerly missing producer, consumer and UI integration. Their mechanisms remain useful, but “future”, “not implemented” and “current” must be read at their original dates. Stable Q001–Q007 are retained.

## Historical questions and answers

## Rust Event Relay technical interview study guide

## Current engineering update — Milestone 2.5, 2026-10-12

The [separate Rust worker](../architecture/milestone-2-5.md) composes validated configuration, JSON tracing, a dedicated PostgreSQL pool/repository and RabbitMQ lifecycle. [Application scheduling](../../../../../../../rust-event-relay/backend/src/application/worker.rs) uses static dispatch and controlled dependencies; [composition](../../../../../../../rust-event-relay/backend/src/bin/relay.rs) constructs concrete infrastructure. It admits one delivery at a time, creates no worker tasks and obtains a fresh acquisition token per invocation. NoEvent paces one invocation, without proving an empty backlog. Confirmed acceptance plus Applied completion alone permits immediate next admission.

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

[Controlled tests](../../../../../../../rust-event-relay/backend/tests/worker.rs) prove scheduling/lifecycle policy; [isolated real composition](../../../../../../../rust-event-relay/backend/tests/worker_smoke.rs) verifies delivery/completion and Supervisor named/collective operation. Happy-path evidence is not crash/recovery evidence. Shared ownership migration remains pending, relay autostart is false and /health proves HTTP liveness only. Configuration/setup failures terminate with sanitized diagnostics; RabbitMQ runtime outages reconnect explicitly. Only the app image/container was updated, preserving shared infrastructure/state.

Transferable reference for future Viva Bem improvements: bound admission, keep infrastructure construction outside scheduling, separate external acceptance from durable completion, preserve uncertainty and primary/cleanup errors, and plan finite cleanup. This is a future engineering reference; no claim is made that Viva Bem uses this architecture, and no private implementation is described or modified. An optional graphical interface belongs after core completion if a concrete operational need exists. Next Rust scope: 2.6 integrated crash/failure/recovery experiments and milestone closure, with no throughput/fairness/consumer-effect or end-to-end at-least-once claim.

Earlier dated sections retain historical scope and are superseded on worker status by this update.


## Current 2.4 interview update — 2026-10-12

Question: What happens when broker acceptance succeeds but completion fails?

**Answer:** The callable `deliver_once` use case returns `Published` with the original claim and separate completion result. Only `Ok(Applied)` means acknowledged durable completion. OwnershipLost and persistence errors, including CommitUncertain, do not cause another send or release. Recovery may duplicate the stable event ID. Publication failures instead retain both the original error and cleanup result; definitive failures release once, Uncertain retains the lease. Cancellation can conceal effects without returning an error. See the [current dossier](../architecture/overview.md) for ports, lease limits and evidence.

Follow-up: Is this a running relay worker? No. 2.4 is a callable use case; 2.5 composes/operates polling, publisher lifecycle/reconnection and Supervisor. 2.6 tests end-to-end crash/recovery. Earlier sections retain their milestone scope.


[English](index.md) | [Português brasileiro](../../pt-BR/faq/index.md)

This portfolio studies reliable event delivery under failure. Current facts come from the [README](../../../README.md), [architecture](../architecture/overview.md), [ownership milestone](../architecture/milestone-2-3.md) and source. First-person answers describe implementation, not production experience. Alternatives are learning comparisons; ADR 007 separately records the selected ownership decision. The 2026-10-10 audit executed no runtime checks. This 2026-10-12 update uses the separately recorded Milestone 2.3 validation; see the [current dossier](../architecture/overview.md).

## 1 Overview and current scope

**Question: Is this already a delivery engine?**

**Model answer:** “The HTTP binary currently loads configuration/tracing and serves liveness with graceful shutdown. Separate modules provide an event envelope, PostgreSQL pending-event reader, confirmed RabbitMQ publisher and ownership models/contracts/schema and production PostgreSQL mutations. No worker connects acquisition, publication and completion yet. Reliable end-to-end delivery, retries and dead-letter handling remain future work.”

Milestones 2.1 publisher, 2.2 ownership types/ports/migration and 2.3 PostgreSQL operations are implemented. 2.4 orchestration, 2.5 worker/composition and 2.6 crash experiments are deferred. Study documents do not change those progress markers.

## 2 Architecture and execution paths

`main.rs` → config/telemetry → TCP listener → `application::serve`. `/health` returns `ok\n`; it does not connect to PostgreSQL/RabbitMQ or prove readiness. Shutdown uses SIGINT/SIGTERM on Unix. Injected shutdown futures let lifecycle tests use an ephemeral socket without global signal manipulation.

Separate data path: an injected `PgPool` backs `PostgresOutboxRepository::read_eligible`; it executes a bounded parameterized SELECT, restores validated envelopes and returns snapshots. `RabbitMqPublisher` implements the application-owned `EventPublisher`, owns a connection/channel, declares durable topology and publishes persistent JSON with stable event ID and confirms. Neither adapter is called by the HTTP binary.

[Persistence contracts](../../../../../../../rust-event-relay/backend/src/persistence/ownership.rs) expose native Send futures with static dispatch. SQLx/Lapin types stay in infrastructure; domain types validate invariants. Small contracts make responsibilities/test seams explicit, with generics/static dispatch rather than a runtime plugin registry. A boxed/dynamic contract could enable runtime adapter selection at allocation/dispatch cost; it has not been implemented here.

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

Opt-in PostgreSQL tests own isolated generated databases and verify reads, original migrations and the ownership up/down migration. Real RabbitMQ tests cover routing/confirm and timeout/cancellation uncertainty. The checked-in CI has default, PostgreSQL and RabbitMQ jobs, but workflow presence is not evidence of a successful remote run. [Historical validation](../testing/validation-results.md) records prior executions; none were repeated here. Milestone 2.3 adds 12 real PostgreSQL ownership cases, including disjoint concurrent claims, held-row skipping and post-lock expiry rejection; pure/fake tests alone establish none of those guarantees. An isolated proxy also tests lost acknowledgement after observed server COMMIT; cancellation during COMMIT remains unverified.

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


## Integrated recovery — Milestone 2.6 follow-ups

### Why can confirm-before-processed still duplicate?

RabbitMQ and PostgreSQL do not share a transaction. Case B confirmed acceptance, then the process died before completion. The row stayed pending; a restarted worker recovered after expiration and published the same ID. Confirm-before-complete prevents completion without confirmed acceptance but leaves a crash window between systems. Consumers need duplicate handling; this experiment does not implement business idempotency.

### What does CommitUncertain establish?

Only that the caller lacks a known durable acknowledgement. This proxy lost the response after observing server COMMIT; an independent pool saw processed and restart did not acquire. Another uncertain schedule can differ. Avoiding blind release/republication prevents compensating a completion that already occurred; inspection/reconciliation needs independent evidence.

### Does a fresh token prevent an old worker from publishing?

No. A's completion/release were rejected while B held a new token, but the former publisher still sent the original envelope. SQL protects a local transition; RabbitMQ does not validate that token. An expired lease does not stop a process. Separating durable authority from external fencing explains duplicates even without overlapping live SQL ownership.

### How can concurrency be supported beyond message counts?

Hold completion with an isolated advisory lock, start two binaries, and inspect two committed distinct tokens/count 1/live leases and two SQL waits. Inspect the exact broker ID set independently, release the barrier and verify processed. This supports the observed schedule, without inferring fairness, business ordering or universal duplicate absence.

### When is at-least-once foundation a defensible description?

When implementation and experiments connect valid durable source events, recoverable pending work and confirmed acceptance before completion. Qualify it with eventual availability, running/restarted workers, resolvable failures, supported storage and downstream duplicate handling. Exclude poison events, permanent rejection, exhausted counters, power-loss behavior and untested exactly-once effects. State which processes are original and which adapter/lifecycle boundaries are instrumented so the claim can be reviewed.

[Evidence and boundaries](../architecture/milestone-2-6.md) | [Acceptance and assumptions](../operations/milestone-2-review.md).

## Durable integration — Milestone 3.3

[Contextual decisions, unbiased jitter, separate pacing, finite maintenance and cancellation](../adr/008-durable-failure-policy.md). Application integration is implemented and tested on isolated infrastructure; shared rollout remains pending. Prior milestone descriptions are historical. General poison scanning remains 3.4, replay 3.5 and full closure 3.6.

## Final local scope questions

[Current implementation dossier](../architecture/overview.md)

### Q008 — Introductory: What is now real in the UI?

**Answer:** The producer, relay and inventory consumer execute real local work. A new run creates producer fact/outbox atomically and normally changes stock 10 to 15. Duplicate and concurrent duplicate actions republish the original envelope, retaining one effect and stock 15. One controlled before-send rejection exercises persisted retry. Crash/race/lost-confirmation or ACK animations are educational playback; they do not shut down infrastructure. Actual kill, reconnect and ambiguous-outcome schedules belong to isolated integration tests.

Follow-up: Why retain simulation? It exposes timing and uncertainty without unsafe global controls. Explain its educational value while explicitly distinguishing persisted facts from illustrated steps.

### Q009 — Intermediate: How does producer idempotency differ from consumer deduplication?

**Answer:** The producer keys fixed intent by request UUID: the same intent resolves to the existing run, while changed intent conflicts. Its one database transaction records goods receipt, initial stock fixture and outbox, preventing a committed fact without its handoff record. The consumer instead keys a durable receipt by consumer name/event ID and validates immutable content. It commits that receipt and stock effect together. A client can lose the producer response after commit; inspection with the same identity is safer than creating another intent. Neither boundary makes transport exactly once.

Follow-up: Would an external email/payment effect share the consumer transaction? No. It needs a separately specified idempotency or durable handoff protocol; this project only demonstrates local stock mutation.

### Q010 — Challenging: Why count acquisitions rather than messages sent?

**Answer:** The durable fact is a committed acquisition, including a crash before send; a worker cannot reliably count all externally accepted messages across lost acknowledgements. Lifetime attempt_count never resets. Retry cycle baseline/maximum define the remaining allowance, while revision and fresh token protect current transitions. A lease that expires enables another acquisition but cannot stop the old process publishing. Thus the counter is neither a broker-message count nor proof of exclusive external activity.

Follow-up: Can replay erase exhaustion? Authorized replay starts a new cycle with expected state/revision and an audit request, preserving lifetime history and original event identity. Storage limits and invalid history remain limits; it is not unrestricted repair.

### Q011 — Challenging: How do concurrent duplicates avoid applying two increments?

**Answer:** The unique receipt insertion precedes stock mutation in READ COMMITTED. Only the winning identity insertion applies the effect and completes the receipt. Another insertion waits on the conflict; a fresh statement then observes the committed winner and compares restored immutable event content. Equal content returns Duplicate without increment; different content is not accepted as the same event. Deferred completeness prevents a partial receipt commit. Retention of identity is part of correctness, not optional cleanup.

Follow-up: Why store BYTEA instead of just a hash? Versioned representation supports restoration and checked model equality without relying only on digest collision assumptions or JSONB normalization. It costs storage and validation. Database-owner tampering remains outside these application safeguards.

### Q012 — Challenging: What do confirms, processed state, receipts and ACKs prove?

**Answer:** A confirm establishes publisher-observed broker acceptance. processed_at records an ownership-protected relay transition. A completed consumer receipt establishes the local stock effect. The consumer then attempts ACK send; success does not establish broker receipt of ACK. These facts can be observed in different orders. Crash after confirm before processed can republish; crash after consumer commit before broker settles ACK can redeliver. Stable event identity plus retained receipt prevents a second supported local effect, not duplicate transport.

Follow-up: What does unknown mean? A missing acknowledgement proves neither commit nor rollback. Preserve identity, inspect independently and avoid compensation/resend based solely on timeout. A snapshot that lacks a receipt also cannot exclude a later commit.

### Q013 — Intermediate: Why is quarantine not simply NACK-and-drop?

**Answer:** The consumer application preserves rejected/unsupported/conflicting input through a confirmed quarantine publication before ACKing the source. Preservation failure or unsupported exact preservation leaves source unsettled for recovery. It separates primary processing evidence from secondary preservation/ACK failure. SQL dead_letter is a relay terminal record, not this RabbitMQ quarantine topology. A broker dead-letter policy would be a different protocol with different evidence and failure windows.

Follow-up: Can quarantine itself duplicate? Yes: confirmed preservation followed by unknown source ACK may repeat on redelivery. Preservation avoids intentional loss; it does not make two AMQP operations atomic.

### Q014 — Intermediate: How do you inspect history without triggering work?

**Answer:** GET history/run evidence and action selection load statement snapshots with observed_at. They do not submit producer intent or repeat an action. Failed refresh retains earlier observations; after 15 seconds they are stale. Sequential bounded polling/timeout and closing the modal control observation only. Run/action/event correlations distinguish duplicate classification from unrelated queue traffic. Capped observation counts are lower bounds. Bearer/origin/client-header checks restrict a local HTTP interface; session storage contains IDs, not the token.

Follow-up: Why not auto-resend unknown actions? The prior action may already have published or committed. A new action is explicit new work; GET inspection cannot resolve every distributed uncertainty and must not pretend it can.

### Q015 — Challenging: What can you defend about tests, operation and capacity?

**Answer:** Pure/fake tests establish policy and call sequencing; isolated PostgreSQL/RabbitMQ/process tests cover selected real failure schedules; browser tests cover real and illustrative UI separately. The final 2026-10-17 manifest records acceptance at its own base, not the current documentation revision or remote CI. The supported single main launcher, separate runtime/test artifacts and named Supervisor controls address local operation. Finite resource/retention bounds reject excess work instead of deleting evidence. They are not measured production capacity, disaster recovery or HA/TLS.

Follow-up: What would justify a production claim? Explicit transport security, least-privilege deployment, retention/restore across database and broker, operational ownership and workload-specific evidence. These are hypothetical improvements, not acceptance blockers retroactively added to the completed local portfolio scope.
