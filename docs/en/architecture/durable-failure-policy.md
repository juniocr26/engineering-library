[Other language](../../pt-BR/architecture/durable-failure-policy.md)

# Failure classification, durable retries and replay identity

## General engineering principles

An error category describes technical evidence at a boundary, not a universal operational retry rule. Serialization can reflect content or implementation; unroutability can reflect repairable topology; outage is not proof of permanent invalidity. Policy must combine phase, known/uncertain effects, authority, remaining budget and independently verified permanence. Preserve primary failures and secondary cleanup outcomes separately.

A durable retry persists a due time atomically with diagnostics and release of valid authority. In-memory waits disappear on restart. Choose authoritative time, precision, bounded jitter and checked arithmetic explicitly. Keep infrastructure recovery separate from event-level schedules. Avoid hidden adapter retries. Unknown acceptance or COMMIT outcome is not nonacceptance/rollback: observe exact state where possible, otherwise recover under durable predicates with duplicate risk. A named reconciliation policy is not an implemented reconciliation capability.

Budget alternatives count different facts: committed acquisitions are durably observable but include pre-send crashes; external publication/acceptance is not atomically measurable with local storage without additional protocol; recovery cycles allow renewed intent while preserving lifetime history. Budget exhaustion is an operational decision, not proof of poison or successful delivery. Application allowance and numeric storage capacity are separate limits; never wrap or silently saturate history.

Poison isolation requires evidence and preserved events. An existing terminal state avoids lifecycle movement; a separate quarantine store improves access separation but needs atomicity and replay consistency. A mechanism requiring a valid owned envelope cannot isolate every malformed stored row: a protected raw-row maintenance path is needed. Prevent repeated poison obstruction of independent valid work, protect live owners, retain sanitized diagnostics and restrict raw evidence. Broker DLQ cannot quarantine rows that never reach the broker.

Replay is explicit auditable intent with expected-state/revision checks, stable original identity, preserved lifetime counters and a defined cycle allowance. Concurrent/repeated requests and lost COMMIT acknowledgements need durable request identity and lookup. Replaying the same event ID may intentionally do nothing in a consumer that already atomically committed its deduplication record and business effect. Renewed delivery does not promise renewed business effect.

## Selected Rust design — 2026-10-12

[ADR 008](../../../../rust-event-relay/docs/en/adr/008-durable-failure-policy.md) and the [complete matrix/roadmap](../../../../rust-event-relay/docs/en/architecture/milestone-3-1.md) choose 10 committed acquisitions per cycle, initial baseline zero, preserved lifetime attempt_count and a new audited cycle on replay. Planned schedules use PostgreSQL post-lock UTC time, whole microseconds, base 1 s/cap 300 s and equal jitter from half-ceiling rounded up to ceiling. No retry hints. Uncertain publication retains its lease; failed/uncertain completion permits no compensating release or blind send. These are project choices, not universal defaults.

Planned isolation uses existing dead_letter plus evidence/audit and raw-row maintenance with revision/lease checks. Replay accepts only valid terminal envelopes, preserves ID/content, and rejects exhausted i32 capacity. Milestone 3.2 adds schema and protected transitions; 3.3 integrates policy; 3.4 implements poison isolation; 3.5 explicit replay; 3.6 integrated evidence/closure. Only pure budget/backoff calculations and tests exist in 3.1. No durable scheduling, quarantine scanner, replay API or consumer is claimed. Vue scenarios remain illustrative. Historical Milestone 2 recovery evidence remains valid within its scope.

The library change is documentation only; its applications, dependencies and runtime remain unchanged. Pure policy tests cannot prove storage durability or concurrent recovery. Production access/retention and shared migration rollout remain separate prerequisites.
