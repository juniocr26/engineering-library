## Presentation prototype — 2026-10-12

The approved blue design is rebuilt as typed Vue components, without the HTML export wrapper. The landing page fills the viewport with decorative artwork and a compact scenario launcher. A native modal keeps the landing visible behind its backdrop, contains and restores focus, supports Escape/Close, blocks background interaction and body scrolling, and scrolls internally on small screens. Shared CSS tokens centralize the design. Reduced motion removes animation while retaining readable step progression.

`BaseButton`, `BaseSelect`, `BaseModal`, `ScenarioLauncher`, `ScenarioExperience`, `StageProgress`, `MessageFlow`, `ActivityPulse`, `EnvelopePreview` and `EventOutput` divide reusable responsibilities. Typed fixtures remain separate from rendering; `usePlayback` owns the cancellable timer, cleaning it up on close/unmount/replay. Each step lasts 3.6 seconds for reading, independent of simulated event timestamps. This is local presentation with no API calls or infrastructure execution.

Five scenarios illustrate confirmed delivery, post-confirmation crash/recovery, competing workers, lost completion acknowledgement and future consumer idempotency. Interrupted, skipped, uncertain and future states retain explicit labels. Broker acceptance is not consumer processing; recovery can republish the same ID; tokens protect database transitions rather than external publication. CommitUncertain alone proves neither commit nor rollback. The lost-ack scenario independently observes a committed result. Atomic consumer deduplication plus a local database effect is planned, not implemented; an external effect does not automatically share that transaction. Future integration needs separately agreed API adapters and actual backend observations. See the [component and browser-test guide](../../../../rust-event-relay/frontend/README.md).

## Structural preparation — 2026-10-12

`frontend/` owns Vue presentation; `backend/` owns Rust models, interfaces, use cases, repositories and adapters. General principle: dependencies point inward and browser presentation must not duplicate delivery authority. Project choice: preserve Rust module names and focused ports, avoid empty layers and root Cargo workspace. Dockerfile: `docker/Dockerfile`; physical Supervisor config: `docker/supervisor/normal.conf`; root Compose and shared caches/data remain in place. Supervisor manages http/relay processes, not broker queues. `start all` starts relay even with autostart=false: shared rollout remains pending.

See [bilingual project setup](../../../../rust-event-relay/docs/en/guides/frontend-backend.md) and [frontend guide](../../../../rust-event-relay/frontend/README.md). The Vue presentation prototype is implemented; Milestone 3 remains a separate scope. Shared PostgreSQL/RabbitMQ preserved; management stays localhost:15672. HTTP/API authentication is checked separately from untested browser form login. No Engineering Library application code/dependencies/runtime were changed. All isolated recovery and Supervisor suites passed; .env/broker credential divergence remains an explicit operational limitation, with existing container credentials used privately for validation.

# rust-event-relay: implementation dossier

## Current engineering update — Milestone 2.5, 2026-10-12

The [separate Rust worker](../../../../rust-event-relay/docs/en/architecture/milestone-2-5.md) composes validated configuration, JSON tracing, a dedicated PostgreSQL pool/repository and RabbitMQ lifecycle. [Application scheduling](../../../../rust-event-relay/backend/src/application/worker.rs) uses static dispatch and controlled dependencies; [composition](../../../../rust-event-relay/backend/src/bin/relay.rs) constructs concrete infrastructure. It admits one delivery at a time, creates no worker tasks and obtains a fresh acquisition token per invocation. NoEvent paces one invocation, without proving an empty backlog. Confirmed acceptance plus Applied completion alone permits immediate next admission.

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

[Controlled tests](../../../../rust-event-relay/backend/tests/worker.rs) prove scheduling/lifecycle policy; [isolated real composition](../../../../rust-event-relay/backend/tests/worker_smoke.rs) verifies delivery/completion and Supervisor named/collective operation. Happy-path evidence is not crash/recovery evidence. Shared ownership migration remains pending, relay autostart is false and /health proves HTTP liveness only. Configuration/setup failures terminate with sanitized diagnostics; RabbitMQ runtime outages reconnect explicitly. Only the app image/container was updated, preserving shared infrastructure/state.

Transferable reference for future Viva Bem improvements: bound admission, keep infrastructure construction outside scheduling, separate external acceptance from durable completion, preserve uncertainty and primary/cleanup errors, and plan finite cleanup. This is a future engineering reference; no claim is made that Viva Bem uses this architecture, and no private implementation is described or modified. An optional graphical interface belongs after core completion if a concrete operational need exists. Next Rust scope: 2.6 integrated crash/failure/recovery experiments and milestone closure, with no throughput/fairness/consumer-effect or end-to-end at-least-once claim.

Earlier dated sections retain historical scope and are superseded on worker status by this update.


## Current engineering update — Milestone 2.4, 2026-10-12

The Rust library now offers [one-attempt delivery orchestration](../../../../rust-event-relay/docs/en/architecture/milestone-2-4.md), implemented in [application/delivery.rs](../../../../rust-event-relay/backend/src/application/delivery.rs). It calls focused acquisition/publication/transition ports with static dispatch and native Send futures. The use case owns sequencing and a basic release policy; infrastructure owns SQL transactions and AMQP. No forwarding service or generic workflow engine is needed. The HTTP binary still composes no worker.

General principle: separate acknowledged authority, confirmed external acceptance, durable local completion and consumer effects. The Rust use case publishes the borrowed original envelope only after acknowledged acquisition, then completes only after the publisher reports confirmed acceptance. `Published` is a fact about the broker; delivery success additionally requires completion `Ok(Applied)`. Neither establishes consumer processing or exactly-once effects. A completion error after acceptance can produce duplicate publication on later recovery, preserving the stable event ID.

General principle: cleanup must not erase the primary failure. `PublicationFailed` retains the original PublishError and an independent `ReleaseOutcome`. Release can acknowledge application, lose ownership, fail or have an uncertain commit. General uncertainty cannot be treated as proof of rollback or nonacceptance. Acquisition CommitUncertain returns no claim and prevents publication; completion CommitUncertain follows known acceptance and may conceal processed state. Repeating either operation blindly is unsafe.

Project choice: Unavailable and Serialization are before-send failures; Unroutable and Rejected are definitive broker failures. Each triggers one ownership-protected release. Uncertain retains the lease, delaying recovery without reconciling acceptance or eliminating duplicates. RabbitMQ retires its uncertain channel, so future composition must replace it. Release preserves availability, attempt count and diagnostics; immediate eligibility can cause rapid repeated failure without a worker scheduling policy. No hidden retry/reacquisition/reconnection exists.

General principle: leases recover abandoned claims but cannot fence an external publisher. PostgreSQL remains authoritative after locks; application wall-clock checks are omitted. Acknowledged acquisition may return expired. Cancellation during acquisition can conceal a committed lease; after acquisition it can abandon a claim; during publication it can conceal acceptance; after acceptance it can leave pending state; during completion/release commit it can conceal applied transitions. Dropping a future may yield no typed error and proves neither rollback nor nonacceptance. There is no detached cleanup or asynchronous Drop; recovery relies on durable expiration.

Five [use-case fake tests](../../../../rust-event-relay/backend/tests/delivery_use_case.rs) cover exact envelope preservation, every publication and transition category, original/cleanup error preservation, confirmation gating, cancellation with explicit synchronization and Send/static dispatch. They demonstrate application ordering and forbidden subsequent calls, not real database rollback or broker nonacceptance. See [dated Rust evidence](../../../../rust-event-relay/docs/en/testing/validation-results.md#milestone-24--2026-10-12) and 2.4 handoff (absent in the 2.5 checkout). Next is **2.5 worker composition and operation**, including polling, publisher lifecycle/reconnection and Supervisor integration; **2.6** covers end-to-end crash/recovery experiments. No end-to-end delivery or performance claim is made.

Earlier dated sections retain their recorded scope; statements that 2.4 orchestration is absent are superseded by this update.


[English](rust-event-relay.md) | [Português brasileiro](../../pt-BR/architecture/rust-event-relay.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

## Current engineering update — Milestone 2.3, 2026-10-12

The Rust repository now implements acquisition, completion and release through its existing ports, with 12 passing isolated PostgreSQL integration cases. The [implementation and decision points](../../../../rust-event-relay/docs/en/architecture/milestone-2-3.md), [dated validation](../../../../rust-event-relay/docs/en/testing/validation-results.md#milestone-23--2026-10-12) and continuity report (pt-BR) (file absent in the 2.4 checkout) distinguish current evidence from the historical review below. The development database was inspected through read-only schema/migration metadata: ownership migration remains pending. No library application code, dependencies or infrastructure changed.

### General principles illustrated by the Rust adapter

A durable lease records temporary authority in storage, allowing recovery after a worker disappears. Stable event ID identifies the original envelope; a fresh ownership token identifies an acquisition. Expiration revokes database transition authority even before another worker acquires. A token does not revoke external sends unless the destination implements fencing. Here RabbitMQ does not fence ownership tokens; broker acceptance followed by failed/uncertain completion can still produce duplicates. Database correctness is not an end-to-end delivery guarantee.

Short transactions separate claiming state from remote publication waits. Row locks serialize changes to each candidate while held; leases persist authority after commit. The Rust adapter explicitly uses Read Committed and selects one due pending candidate with FOR UPDATE SKIP LOCKED, filtering live leases and exhausted counters. This keeps independent acquisitions disjoint under the tested contention and skips an eligible row held by another transaction. Empty acquisition means no row acquired by that call, not absence of backlog; SKIP LOCKED is neither a fair queue nor a general consistent observation mechanism. Observation remains a separate read-only contract and includes leased/exhausted pending rows.

Authoritative time must be sampled **after obtaining locks**: waiting can outlive a lease. PostgreSQL now() fixes transaction-start time, whereas clock_timestamp() samples actual server time. The adapter first samples a selection cutoff, then obtains a candidate lock, restores data and samples the decision clock to recheck eligibility and set timestamps. Completion/release lock by ID before taking the clock sample and conditionally require pending plus matching token and acquired_at <= time < expires_at. At exact expiry the owner is rejected; a clock before acquired_at also rejects. No monotonic clock guarantee is assumed. Commit/response latency consumes lease duration; returning an acknowledged claim does not guarantee remaining validity.

Pre-commit failure, ordinary ownership conflict and unknown commit are distinct. Invalid selected data fails without silently skipping or repairing it; a malformed candidate can repeatedly impede progress. Ordinary server-reported COMMIT rejection is known failure, demonstrated with an isolated deferred constraint trigger. Loss of acknowledgement may hide a committed change: the adapter conservatively maps commit transport/protocol errors and completion-unknown codes to CommitUncertain. After uncertain acquisition, do not publish from an unconfirmed claim; inspect durable ownership or let expiry recover with a fresh token. After uncertain completion, processed may already be durable, so blindly republishing or equating conflict with previous success is unjustified. Cancellation can leave no returned classification at all; SQLx queues rollback on dropping an open transaction but cannot undo a committed operation or promise immediate rollback.

Project-specific choices should not be generalized as universal policy: one event per acquisition, request-generated token, microsecond leases, leased rows remaining pending, attempts counting committed acquisitions up to i32::MAX, exclusion of exhausted candidates, repeated completion/release returning OwnershipLost, and release preserving availability/diagnostic instead of calculating backoff. Completion persists the caller's confirmation decision without contacting the broker. Pool deadlines, retry/DLQ policy and reconciliation/orchestration remain caller/future-use-case responsibilities.

### What the tests establish and leave open

Real PostgreSQL evidence covers disjoint competing acquisitions, held-row skipping, stale/wrong/missing/terminal/repeated owner rejection, expired-token replacement, metadata/envelope preservation, invalid-data and duration-overflow rollback, counter exhaustion, atomic field clearing, immediate SQL rejection and deferred COMMIT rejection. The expiration test explicitly observes a row-lock wait, refreshes pg_stat_activity snapshots, verifies transaction start before expiry, waits until database time reaches expiry and then unlocks; both completion and release reject. A cancellation case covers a blocked pre-mutation future and subsequent pool usability. A one-microsecond lease demonstrates expiry by the time an acknowledged acquisition is observed.

Exact expiration equality is deterministic model evidence, not a controlled equality experiment against the real database clock. An isolated connection proxy now discards CommandComplete COMMIT after observing server completion for acquisition, completion and release: the adapter returns CommitUncertain while an independent connection observes committed state. It proves this committed uncertain outcome is possible, not that all uncertain outcomes imply commit or rollback. Shared services and application traffic are untouched. Cancellation during COMMIT remains unverified. The pre-acquired_at case is a future-timestamp fixture, not a real clock reversal experiment. Tests do not establish fairness, throughput, every write schedule, power-loss durability, remote CI or end-to-end delivery. Milestone 2.4 next composes one claim → publish → persist outcome; polling, worker Supervisor/reconnection, backoff/DLQ, producers and consumer idempotency are later scope.

## Historical dossier — static review on 2026-10-10

The remaining sections record the previous scope. Statements about absent production ownership SQL are historical and superseded by the update above; broker/HTTP and production-operational limitations still apply.

## Verified publisher integration

The callable RabbitMQ adapter implements the application-owned `EventPublisher` port. It opens an owned connection/channel, declares a durable direct exchange and durable queue, binds with the configured routing key and enables publisher confirms. Defaults are `relay.events`, `relay.local` and `event`. It serializes the event envelope to JSON, uses stable event identity as message ID, sends persistent messages with mandatory routing and waits for confirmation. A successful Ack without return proves broker acceptance under this contract; it does not prove consumer processing, business effects or an end-to-end relay guarantee. No consumer is implemented.

`RabbitMqConfig` constructs an escaped AMQP URI from separate credential/vhost fields, validates names and deadlines, and redacts Debug. The current configuration accepts `amqp`, not `amqps`; there is no verified production TLS path. Authentication uses broker credentials/vhost, not HTTP application authentication or payload encryption. Local Compose supplies broker storage and a management endpoint; management login is a separate operational boundary from publishing.

The publisher mutex serializes one in-flight publication. Admission waiting and publication waiting have separate deadlines; setup and close are also bounded. Serialization/unavailable, rejected, unroutable and uncertain are distinct outcomes. Timeout/error/cancellation after sending begins can leave broker acceptance unknown; the adapter retires the channel and requires explicit reconnection. It performs no automatic retry. A database lease token is not sent as a broker fencing mechanism and cannot stop a stale process's external send.

The PostgreSQL reader, ownership ports and this publisher are separate library paths. `main` only composes config/tracing/HTTP liveness. There is no producer transaction, polling worker, acquisition SQL, completion SQL, consumer effect or payment integration connecting them. Proposed acquisition → publish → complete remains hypothetical orchestration. A diagram that connects these adapters as a running worker would be inaccurate.

## Authority, diagnostics and transport

The HTTP API is only `GET /health`, a fixed liveness response without dependency checks or login. Structured JSON tracing is configured by `RUST_LOG`. Persistence and publication errors expose sanitized Display/Debug categories while retaining typed source chains. Printing those sources may disclose connection details, SQL or payload data; safe outer formatting is not full log redaction. The review never read live credentials or application rows.

Ownership tokens authorize future conditional database transitions, not data confidentiality. Event UUID identifies a stable event across retries; ownership token identifies one acquisition. Pure delivery models reject zero/invalid tokens, incoherent times, stale owners and exact-expiry transitions. Nullable migration fields must be absent together or form a coherent pending lease. SQL constraints validate row shape; they do not prove transition history, correct clock sampling or concurrent ownership enforcement. Those require production mutation implementations and PostgreSQL concurrency tests, currently absent.

Short transactions and publication outside locks are the recorded ADR 007 design. A future completion/release must match event ID, token, pending state and an unexpired lease using database time after lock acquisition. Broker publication remains a separate boundary: the token cannot revoke a send already underway. End-to-end duplicate-tolerant effects would need consumer deduplication coupled with business changes. This is theory for future work, not an implemented consumer. Current AMQP is plaintext transport; durable storage and UUIDs do not supply application encryption, authentication signatures or production TLS.

## Deployment, observability and evidence gaps

Compose supplies local PostgreSQL, RabbitMQ and a development app managed by Supervisor. The HTTP process waits for config/tracing/listener setup; it does not create a PgPool or RabbitMqPublisher. Container dependency health can gate startup but `/health` remains process liveness. Supervisor allows 30 s for HTTP drain and Compose grants 35 s for manager shutdown. Source changes require stop/build/start; auto-reload and a deployed worker are absent. Bind/named storage survives ordinary recreation, not host/storage loss.

SQLx migrations are versioned and explicitly applied, not applied automatically by HTTP startup. Preserve migration IDs and existing applied content. The ownership migration is source plus isolated test evidence; the previous milestone record says it remained pending in the shared development database. This review did not inspect that database or update its status. A down migration removes ownership columns; earlier downs can destroy the outbox. Neither down nor reapplying schema restores rows. A real rollout needs compatibility review and separately verified backup/restore, not a destructive reset.

Default tests validate domain, mapping and contracts plus HTTP/socket behavior. Opt-in PostgreSQL tests create exact generated fixture databases and verify cleanup; broker tests exercise routing and uncertainty. Some database-independent tests use local sockets, so independent does not mean no I/O. CI workflow presence is configuration evidence, not proof of remote success. Historical results remain in testing/validation-results. No Rust build, test, Docker call, migration, broker request or benchmark ran in this review.

Performance is currently constrained by bounded row counts and one-in-flight publisher admission, but row count does not bound payload bytes. Reader `fetch_all` materializes a batch; invalid selected data fails the whole result and can block future repeated reads. No quarantine, backpressure policy, polling rate, throughput measurement, metrics endpoint or production pool sizing is delivered. Remaining evidence gaps: ownership SQL/concurrency, worker orchestration, duplicate/recovery experiments, poison-row policy, production TLS/HA, retention/backup restore and performance. These are not prerequisites already demonstrated by a green liveness probe.

## Supporting evidence

- [integrations/rabbitmq-contract](../../../../rust-event-relay/docs/en/integrations/rabbitmq-contract.md)
- [security/diagnostic-and-authority-boundaries](../../../../rust-event-relay/docs/en/security/diagnostic-and-authority-boundaries.md)
- [operations/deployment-and-evidence](../../../../rust-event-relay/docs/en/operations/deployment-and-evidence.md)
- [Interview / Entrevista](../interviews/rust-event-relay.md)


## Milestone 2.6 — Demonstrated recovery, 2026-10-12

Rust experiments with real PostgreSQL/RabbitMQ and owned processes observed pending state after SIGKILL before send and after confirmation; actual lease expiration followed by fresh token/count 2 and processed. The latter window produced two messages with the original ID. Lost AMQP confirmation left pending/Uncertain while an independent observer already had the message; the worker replaced its connection without replaying the live claim. Lost completion COMMIT response produced CommitUncertain despite durable processed/count 1; restart did not reacquire it.

Two binaries were blocked in completion after publication: distinct durable tokens and live leases support concurrent ownership protection for this schedule. An old owner could not complete/release after B acquired; the former publisher could still send. Database authority protects transitions, not external fencing. SQL rejection/deadlines and TERM cancellation retained recoverable pending work; restored availability/expiration/restart completed it. Observer ACK is fixture behavior, not a business effect.

This evidence supports Milestone 2 implemented-scope closure as an at-least-once foundation with committed source events, supported storage/contracts, eventual availability, a running worker and valid events whose failures resolve. It does not prove universal/exactly-once delivery, fairness, ordering, power-loss behavior, poison/permanent rejection, exhausted counters or productive HA/TLS. Shared rollout stays pending/relay STOPPED. Next: durable retry/classification/quarantine-dead-letter/auditable replay decisions. These principles transfer without claims about another product's private architecture.

[Evidence and boundaries](../../../../rust-event-relay/docs/en/architecture/milestone-2-6.md) | [Acceptance and assumptions](../../../../rust-event-relay/docs/en/operations/milestone-2-review.md).


## Milestone 3.1 — selected policy

[Classification, scheduling, budgets, uncertainty, poison isolation and replay identity](durable-failure-policy.md). General principles are separated from selected Rust defaults; only pure policy calculations exist today.
