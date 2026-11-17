# Server tooling: guarded deployment and runtime custody

## Server architecture — 2026-11-16

Server orchestration retains guarded cleanup of regenerable artifacts while preserving MongoDB, MySQL and Redis storage for either answer to its existing retention question. Parent/nested/resolved-path checks prevent database directories from becoming indirect cleanup targets; the obsolete MongoDB removal action is rejected. Removing destructive script behavior did not delete existing directories. Application server overlays now select externally managed databases; development retains local infrastructure.

[Operational status and limits](../operations/index.md) · [Connection interface](../env/index.md)

Source inspection: 2026-11-04. Implemented behavior is distinguished from executed verification and provider homologation.

Bash orchestration with Python deployment guards for the four server applications: Hub, Portal, Carteira and Cofre. The updater validates roots/Git state, coordinates the audit lock, updates selected branches, provisions existing runtime inputs, builds sequentially, checks readiness and performs narrowly scoped cleanup. It has no automatic all-project rollback.

## Domain boundaries and detailed implementation

The maintained private source chapter covers workflows, persistence, authorization, failure handling and current limitations. Centralization keeps this concept summary separate from operational detail.

- [Server tooling: guarded deployment and runtime custody](../../../../../acesso-servidor/docs/en/architecture/current-implementation.md)
- [Implemented contracts](contracts.md)
