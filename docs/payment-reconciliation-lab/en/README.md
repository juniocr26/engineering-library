# Payment Reconciliation Lab

[English](README.md) | [Português brasileiro](../pt-br/README.md)

A backend engineering lab transitioning toward payment reconciliation with Java, Spring Boot, Angular, PostgreSQL and Stripe. Infrastructure identity is updated; the retained read-only catalog is still the current interface. Reconciliation and Stripe integration remain planned. Purchase discounts and catalog seeding are retired.

## Documentation catalog and reading path

- [Complete categorized catalog](index.md)
- [Review checklist and evidence gaps](operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [Architecture decisions](adr/architecture-decisions.md)
- [Architecture](architecture/overview.md)
- [Development dependencies and recovery](docker/development.md)
- [Docker and configuration](docker/runtime.md)
- [Historical restructuring report](operations/historical-refactor-report.md)
- [Scope and roadmap](architecture/roadmap.md)
- [Setup and execution](guides/setup.md)
- [Testing](testing/strategy.md)
- [Validation results](testing/verification.md)
- [Toolchain](guides/toolchain.md)

[License](../../../../../Portifo%CC%81lio/payment-reconciliation-lab/LICENSE)

## Quick start and scope

For a fresh clone, install Docker/Compose, copy the example and set a private database password before startup:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose up --build -d --wait --wait-timeout 180
```

UI: http://localhost:4200/products; API: http://localhost:8080/api/v1/products. Keep DEV_SEED_ENABLED=false. Existing storage requires the documented identity transition; startup applies migrations. This remains a catalog, with payments planned.

For existing checkouts, update configuration deliberately instead of overwriting the local file.

[Installation, execution flow, operational limits and project interview](guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.
