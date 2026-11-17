# Scoped encrypted requests and card ownership

2026-11-04. All declared domain routes are POST with service JWT and exact method/path/body binding. Links expose insert/get/update; cards have separate credit/debit route families; ratings expose insertion/evaluated IDs/averages. Bank routes are retired. Debit adds a delegated-sub owner check that the base credit Use Case lacks. Manual production debit deletion confirms provider removal; manual credit deletion does not perform that same call. Treat these asymmetries as implementation limitations.

The source repository maintains detailed contracts and source evidence; review was static without database or provider access.

- [HTTP](../../../../../cofre-paciente/docs/en/api/http-contracts.md)
- [Lifecycle / Ciclo de vida](../../../../../cofre-paciente/docs/en/architecture/current-implementation.md)

[Index / Índice](../index.md)
