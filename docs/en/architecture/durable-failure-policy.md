[Other language](../../pt-BR/architecture/durable-failure-policy.md)

# Failure classification, durable retries and replay identity

## General engineering principles

An error category describes technical evidence at a boundary, not a universal operational retry rule. Serialization can reflect content or implementation; unroutability can reflect repairable topology; outage is not proof of permanent invalidity. Policy must combine phase, known/uncertain effects, authority, remaining budget and independently verified permanence. Preserve primary failures and secondary cleanup outcomes separately.

A durable retry persists a due time atomically with diagnostics and release of valid authority. In-memory waits disappear on restart. Choose authoritative time, precision, bounded jitter and checked arithmetic explicitly. Keep infrastructure recovery separate from event-level schedules. Avoid hidden adapter retries. Unknown acceptance or COMMIT outcome is not nonacceptance/rollback: observe exact state where possible, otherwise recover under durable predicates with duplicate risk. A named reconciliation policy is not an implemented reconciliation capability.

Budget alternatives count different facts: committed acquisitions are durably observable but include pre-send crashes; external publication/acceptance is not atomically measurable with local storage without additional protocol; recovery cycles allow renewed intent while preserving lifetime history. Budget exhaustion is an operational decision, not proof of poison or successful delivery. Application allowance and numeric storage capacity are separate limits; never wrap or silently saturate history.

Poison isolation requires evidence and preserved events. An existing terminal state avoids lifecycle movement; a separate quarantine store improves access separation but needs atomicity and replay consistency. A mechanism requiring a valid owned envelope cannot isolate every malformed stored row: a protected raw-row maintenance path is needed. Prevent repeated poison obstruction of independent valid work, protect live owners, retain sanitized diagnostics and restrict raw evidence. Broker DLQ cannot quarantine rows that never reach the broker.

Replay is explicit auditable intent with expected-state/revision checks, stable original identity, preserved lifetime counters and a defined cycle allowance. Concurrent/repeated requests and lost COMMIT acknowledgements need durable request identity and lookup. Replaying the same event ID may intentionally do nothing in a consumer that already atomically committed its deduplication record and business effect. Renewed delivery does not promise renewed business effect.

## Selected Rust design — 2026-10-12

[ADR 008](../../../../rust-event-relay/docs/en/adr/008-durable-failure-policy.md) and the [complete matrix/roadmap](../../../../rust-event-relay/docs/en/architecture/milestone-3-1.md) choose 10 committed acquisitions per cycle, initial baseline zero, preserved lifetime attempt_count and a new audited cycle on replay. Implemented 3.2 scheduling uses PostgreSQL post-lock UTC time, whole microseconds, base 1 s/cap 300 s and equal jitter from half-ceiling rounded up to ceiling. No retry hints. Uncertain publication retains its lease; failed/uncertain completion permits no compensating release or blind send. These are project choices, not universal defaults.

Milestone 3.2 now implements additive retry-cycle/baseline/budget/revision metadata, protected scheduling and preserved dead_letter transitions, and an exact-row exhausted-event maintenance port. General poison scanning remains 3.4; application policy integration is 3.3, authenticated audited replay 3.5 and integrated closure 3.6. No deployed retry pipeline, scanner, replay API or consumer is claimed. Vue scenarios remain illustrative and unchanged. Historical Milestone 2 evidence retains its scope.

## Durable transition mechanics

Store cycle allowance alongside the lifetime count rather than resetting history or relying on volatile configuration. Backfill baseline zero includes historical acquisitions; count >= 10 requires maintenance without a fresh acquisition. The final committed acquisition may complete while its lease is valid. Scheduling cannot bypass budget or numeric storage capacity.

Use a short transaction to lock the exact row, then sample database time in a separate statement and check status, identity, live token, cycle and expected revision. Persist selected delay, sanitized evidence, cleared authority and advanced revision together. Increment revision on acquisition, completion, release and new transitions; external writers must follow the same protocol. Constraints enforce row shape, not operator authority or every historical transition.

The narrow maintenance operation targets one independently observed ID/cycle/revision with SKIP LOCKED, validates due pending and no live lease, and distinguishes acquisition_budget_exhausted from storage_counter_exhausted. It neither constructs a valid envelope nor scans/repairs poison. Terminal rows retain original identity, envelope and counters, have no owner or processed_at, and record reason/time/evidence. Existing dead_letter gets a legacy reason and migration observation time; historical failure time is unknown. No automatic reactivation or retention deletion exists.

Evidence accepts only fixed policy/validator versions, a typed phase and optional UUID reference, within 2 KiB serialized UTF-8 JSON. Preserve legacy diagnostics as restricted data; do not copy arbitrary driver chains, credentials or payload into public evidence. SQL CHECK must reject JSON null explicitly because a nullable result otherwise passes.

A repeat after success conflicts rather than inferring success from no matching row. Lost COMMIT acknowledgement remains CommitUncertain; cancellation can suppress a durable result. Observe exact state before further action rather than recomputing a schedule or blindly publishing again. Isolated real PostgreSQL experiments cover locks, budgets, competing maintainers, server rejection, lost acknowledgement and cancellation after server COMMIT; pure policy tests alone do not prove these properties.

[Rust implementation and rollout contract](../../../../rust-event-relay/docs/en/architecture/milestone-3-2.md) separates these project decisions from general principles. Shared schema rollout, raw-evidence access/retention and production activation remain separately authorized prerequisites. Down loses retry/audit metadata and is tested only on disposable fixtures, never as production recovery. The library change is documentation only; applications, dependencies and runtime are unchanged.
