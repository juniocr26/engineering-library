# Startup, deployment and test boundaries

[English](deployment-and-evidence.md) | [Português brasileiro](../../pt-BR/operations/deployment-and-evidence.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

The base runtime applies Flyway and validates the schema. The development override sets `SPRING_FLYWAY_ENABLED=false`, so it requires an already initialized schema; disabling migrations does not create missing tables. `DEV_SEED_ENABLED=true` activates a runner that deliberately fails startup because reconciliation fixtures do not exist. Keep it false; there is no seed job to retry. Compose waits for database health in the base setup, while the development override disables backend health and changes the frontend dependency to service_started.

Spring liveness includes application state; readiness includes state and database connectivity. Neither tests matching, provider credentials or webhook processing. Angular retry repeats a GET rather than retrying a financial operation. MockMvc tests replace the catalog service, Angular tests replace HTTP and opt-in PostgreSQL integration uses Testcontainers for migrations/constraints/visibility. The current source inventory is 7 backend unit/API methods, 5 PostgreSQL methods and 4 Angular cases; this is not coverage percentage or a new passing result. No application tests ran here.

Preserve initialized database credentials and the actual volume during the infrastructure rename. The existing-db override explicitly reuses an external volume rather than creating a silent replacement. Before a real update, review compatibility, take an independently recoverable backup, stage migration verification and define rollback of code plus forward-compatible schema. None of these runtime procedures were executed here. Reverting an image or a Flyway file is not restoring lost data. Evidence gaps include production rollout/TLS, backup restore, large catalog query plans and the entire reconciliation lifecycle. Payment categories must be marked not implemented, rather than filled with fictional webhook contracts or ledger flows.
