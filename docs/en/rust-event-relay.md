# Rust Event Relay technical interview study guide

[English](rust-event-relay.md) | [Português brasileiro](../pt-BR/rust-event-relay.md)

This portfolio studies reliable event delivery under failure. Current facts come from the [README](../../../rust-event-relay/README.md), [architecture](../../../rust-event-relay/docs/en/architecture.md), [ownership milestone](../../../rust-event-relay/docs/en/milestone-2-2.md) and source. First-person answers describe implementation, not production experience. Alternatives are learning comparisons; ADR 007 separately records the selected ownership decision. No runtime checks were executed in this documentation audit.

## 1 Overview and current scope

**Question: Is this already a delivery engine?**

**Model answer:** “The HTTP binary currently loads configuration/tracing and serves liveness with graceful shutdown. Separate modules provide an event envelope, PostgreSQL pending-event reader, confirmed RabbitMQ publisher and ownership models/contracts/schema. No worker connects acquisition, publication and completion yet. Reliable end-to-end delivery, retries and dead-letter handling remain future work.”

The milestone state is 2.1 publisher and 2.2 ownership types/ports/migration implemented; 2.3 production mutations, 2.4 orchestration, 2.5 worker/composition and 2.6 crash experiments are deferred. Study documents do not change those progress markers.

## 2 Architecture and execution paths

`main.rs` → config/telemetry → TCP listener → `application::serve`. `/health` returns `ok\n`; it does not connect to PostgreSQL/RabbitMQ or prove readiness. Shutdown uses SIGINT/SIGTERM on Unix. Injected shutdown futures let lifecycle tests use an ephemeral socket without global signal manipulation.

Separate data path: an injected `PgPool` backs `PostgresOutboxRepository::read_eligible`; it executes a bounded parameterized SELECT, restores validated envelopes and returns snapshots. `RabbitMqPublisher` implements the application-owned `EventPublisher`, owns a connection/channel, declares durable topology and publishes persistent JSON with stable event ID and confirms. Neither adapter is called by the HTTP binary.

[Persistence contracts](../../../rust-event-relay/src/persistence/ownership.rs) expose native Send futures with static dispatch. SQLx/Lapin types stay in infrastructure; domain types validate invariants. Small contracts make responsibilities/test seams explicit, with generics/static dispatch rather than a runtime plugin registry. A boxed/dynamic contract could enable runtime adapter selection at allocation/dispatch cost; it has not been implemented here.

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

The ports require database time sampled after lock acquisition and known committed acquisition before returning owned data. **These are contracts for future PostgreSQL mutations, not SQL concurrency behavior implemented in the current reader.** The 2.2 migration adds coherent nullable lease fields; constraints prove row shape, not legal transition history or uniqueness of every historical token. `CommitUncertain` means a mutation may have committed; `OwnershipLost` is an ordinary unmatched-authority result. Neither should become assumed success.

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

Opt-in PostgreSQL tests own isolated generated databases and verify reads, original migrations and the ownership up/down migration. Real RabbitMQ tests cover routing/confirm and timeout/cancellation uncertainty. The checked-in CI has default, PostgreSQL and RabbitMQ jobs, but workflow presence is not evidence of a successful remote run. [Historical validation](../../../rust-event-relay/docs/en/validation-results.md) records prior executions; none were repeated here. Pure/fake ownership tests do not establish competing PostgreSQL owner guarantees before 2.3 exists.

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
6. Review tests/CI and historical evidence; separate models/schema from absent mutation/orchestration code.
7. Study 2.3–2.6 prerequisites and duplicate/idempotency failure windows without marking them delivered or studied.
