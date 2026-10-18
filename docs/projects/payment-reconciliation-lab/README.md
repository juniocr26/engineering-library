# Payment Reconciliation Lab

[English](README.md) | [Português brasileiro](README.pt-BR.md)

A backend engineering lab transitioning toward payment reconciliation with Java, Spring Boot, Angular, PostgreSQL and Stripe. Infrastructure identity is updated; the retained read-only catalog is still the current interface. Reconciliation and Stripe integration remain planned. Purchase discounts and catalog seeding are retired.

## Documentation catalog and reading path

- [Complete categorized catalog](docs/en/index.md)
- [Review checklist and evidence gaps](docs/en/operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [Architecture decisions](docs/en/adr/architecture-decisions.md)
- [Architecture](docs/en/architecture/overview.md)
- [Development dependencies and recovery](docs/en/docker/development.md)
- [Docker and configuration](docs/en/docker/runtime.md)
- [Historical restructuring report](docs/en/operations/historical-refactor-report.md)
- [Scope and roadmap](docs/en/architecture/roadmap.md)
- [Setup and execution](docs/en/guides/setup.md)
- [Testing](docs/en/testing/strategy.md)
- [Validation results](docs/en/testing/verification.md)
- [Toolchain](docs/en/guides/toolchain.md)

[License](../../../../payment-reconciliation-lab/LICENSE)

## Quick start and scope

For a fresh clone, install Docker/Compose, copy the example and set a private database password before startup:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose up --build -d --wait --wait-timeout 180
```

UI: http://localhost:4200/products; API: http://localhost:8080/api/v1/products. Keep DEV_SEED_ENABLED=false. Existing storage requires the documented identity transition; startup applies migrations. This remains a catalog, with payments planned.

For existing checkouts, update configuration deliberately instead of overwriting the local file.

[Installation, execution flow, operational limits and project interview](docs/en/guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.

<!-- collection entry -->
## Engineering Library collection

[Library](../../index.md) | [English](docs/en/index.md) | [Português brasileiro](docs/pt-BR/index.md) | [Interview](docs/en/faq/index.md) | [Provenance](docs/en/operations/source-review.md)

Spring Boot/Angular/PostgreSQL foundation with a retained read-only catalog; reconciliation and Stripe are not implemented.
