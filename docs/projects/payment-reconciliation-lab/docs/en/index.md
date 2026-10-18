# Documentation catalog: payment-reconciliation-lab

[Project introduction](../../README.md) | [Other language](../pt-BR/index.md)

Reading path: purpose/setup → architecture/contracts → security/failures → testing/evidence → operations. For the library, use catalog/dossier → project interview → foundations → failure follow-ups. Historical milestone/refactor/handoff records describe their original dates; current review/checklist explains present scope.

## architecture

Components, flows and implemented boundaries.

- [Architecture and domain](architecture/overview.md)
- [Scope and implementation status](architecture/roadmap.md)

## adr

Recorded decisions and consequences; identifiers/history preserved.

- [Architecture Decisions & Trade-offs](adr/architecture-decisions.md)

## guides

Setup, prerequisites and reading procedures.

- [Setup and execution](guides/setup.md)
- [Toolchain](guides/toolchain.md)

## testing

Test strategy, inventories and dated evidence.

- [Testing](testing/strategy.md)
- [Refactor verification — 2026-10-05](testing/verification.md)

## docker

Local images, services, mounts and configuration.

- [Docker development setup and recovery](docker/development.md)
- [Development Docker environment](docker/runtime.md)

## database

Models, constraints, migrations and consistency.

- [Catalog schema and domain transition](database/catalog-and-transition.md)

## api

Exposed contracts and client behavior.

- [Implemented catalog API and UI](api/catalog-contract.md)

## operations

Diagnosis, recovery, review checklists and historical records.

- [payment-reconciliation-lab: Repository completion checklist](operations/completion-checklist.md)
- [Startup, deployment and test boundaries](operations/deployment-and-evidence.md)
- [Aurora Bakery restructuring report](operations/historical-refactor-report.md)

## security

Authentication, authorization, data and resource boundaries.

- [Read API security and future payment boundaries](security/read-api-boundaries.md)

Category applicability and omissions are justified in the [completion checklist](operations/completion-checklist.md). No empty category is created.

## Practical implementation and interview path

[Trace a request, inspect failure boundaries and rehearse answers](guides/implementation-study.md).

<!-- project-first catalog -->
## Complete collection chapters

[Library](../../../../index.md) | [Português brasileiro](../pt-BR/index.md)

Suggested order: README purpose → guides → architecture and ADRs → contracts, data and integrations → security → testing → operations → interview. Missing chapters have no maintained content; they are not promised features. Each chapter lists all its pages.

- [adr](adr/index.md)
- [api](api/index.md)
- [architecture](architecture/index.md)
- [database](database/index.md)
- [docker](docker/index.md)
- [guides](guides/index.md)
- [operations](operations/index.md)
- [security](security/index.md)
- [faq](faq/index.md)
- [testing](testing/index.md)

- [env](env/index.md)
