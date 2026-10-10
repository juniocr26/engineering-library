# rust-event-relay: implementation dossier

[English](rust-event-relay.md) | [Português brasileiro](../../pt-BR/architecture/rust-event-relay.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

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
