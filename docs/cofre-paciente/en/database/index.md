# MongoDB collections and observed deletion

2026-11-04. Current domain collections are cartoes, cartoes_debito, links, avaliacoes_psicologos and media_avaliacoes. Card maps are owner-keyed and store minimal encrypted provider references; they are not a PAN/CVC store. Observed hashes and exact-value compare/delete protect concurrent replacement. Partial/unreadable results differ from empty storage. Single-document atomicity does not extend to SQL or remote provider effects; deployed indexes and legacy formats were not inspected.

The source repository maintains detailed contracts and source evidence; review was static without database or provider access.

- [Collections / Coleções](../../../../../cofre-paciente/docs/en/database/database-audit.md)
- [Lifecycle / Ciclo de vida](../../../../../cofre-paciente/docs/en/architecture/current-implementation.md)

[Index / Índice](../index.md)
