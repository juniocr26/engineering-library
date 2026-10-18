# Scope and implementation status

[English](roadmap.md) | [Português](../../pt-BR/architecture/roadmap.md)

## Current foundation

The Payment Reconciliation Lab infrastructure identity is configured. Spring Boot, Angular, PostgreSQL, preserved Flyway migrations, deny-by-default security and the legacy read-only catalog remain. Catalog purchase/consent policy and seed were retired; their old results belong to the [historical report](../operations/historical-refactor-report.md). Current checked-in tests are described in [testing](../testing/strategy.md).

## Future direction

Payment reconciliation and Stripe test integration remain unimplemented. There is no reconciliation schema, matching algorithm, import/provider adapter, webhook, discrepancy lifecycle or review UI. The previous bakery identity/checkout/loyalty roadmap is historical and does not establish requirements for this new direction.

Suggested prerequisite order for design and study, not approved release milestones or completed work:

1. Define source records, monetary precision/currency, matching criteria and discrepancy semantics.
2. Define ownership/access rules, persistence and immutable audit history before exposing writes.
3. Implement isolated deterministic reconciliation fixtures and tests before provider integration.
4. Define Stripe test adapter, signed event handling, idempotency and replay/recovery requirements.
5. Introduce review UI and operational failure checks only after the backend contracts exist.

These are reasonable next design questions, not evidence that alternatives were evaluated or selected during development. No topics are marked studied or complete. Preserve existing data while replacing legacy domain surfaces through separately reviewed changes.

## Deferred infrastructure

No broker, cache, distributed worker or object storage is currently required by an implemented reconciliation workflow. Introduce them only for explicit delivery, latency, retention or deployment requirements. The development environment is not a production deployment claim.
