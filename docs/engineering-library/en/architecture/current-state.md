# Engineering Library: current architecture

[Architecture index](index.md) · [Detailed implementation](current-implementation.md)

<!-- reading-section: current-state-1 -->
## Documentation layout

Current baseline: 2026-11-26, source `246f58be`. Engineering Library is a private Viva Bem repository for authorized internal use. Historical scaffold and pre-Ollama statements do not describe the current implementation.

| Content | Checkout-relative path |
| --- | --- |
| English chapters | `docs/<slug>/en/` |
| Brazilian Portuguese chapters | `docs/<slug>/pt-br/` |
| Shared / localized images | `docs/<slug>/img/`, language `img/` directories |
| Approved source disclosure catalog | `docs/<slug>/en/links/` |
| Registration metadata | `docs/.catalog.json` and localized bios |
| Private operation/recovery data | `backend/storage/makedocs/` |

API language `pt-BR` maps to directory `pt-br`. PostgreSQL stores metadata and shared annotations; Markdown owns chapter bodies. Rails and Next use `/docs` in Compose, currently writable for both services. Existing annotation identities are logical, not physical book page numbers.

<!-- reading-section: current-state-2 -->
## Implemented foundation

Next.js supplies catalog, measured book pagination, chapter navigation, search, diagrams and approved source disclosures. Rails supplies paginated catalog metadata, shared notes/highlights/bookmarks and guarded development management. PostgreSQL persists those relational records. There are no personal accounts or private per-user annotation datasets.

The local Ollama pipeline, explicit registration, verified relocation, idempotent retries, removal preservation, supervised host filesystem adapter and recoverable two-destination draft publication are implemented. The normal UI and CLI reuse the same documentation command. `/up` checks Rails response plus required host adapter readiness; it does not certify database integrity or semantic output quality.

<!-- reading-section: current-state-3 -->
## Evidence and open limits

MakeDocs is operational, while source coverage, factual wording and translation quality remain limited and require review. No full-book acceptance, production hardening, universal RAG or completed neural fine-tuning is implied. This documentation review uses current source analysis and does not rerun generation or training.

Use the [detailed architecture](current-implementation.md), [development guide](../guides/application-development.md), [MakeDocs pipeline](../training/local-documentation-command.md), [recovery guide](../operations/runtime-and-recovery.md), [decisions](decisions.md) and [technical FAQ](../faq/application-and-catalog.md). Dated audits remain available in [operations](../operations/index.md).

<!-- reading-section: shared-annotation-migration -->
## Shared annotation migration

Historical record retained from the earlier review; row counts are not a fresh database measurement.


On 2026-10-20, the local database retained 60 notes, 60 highlights and 12 bookmarks through the expand/contract migration. Existing IDs, note bodies, ranges and foreign keys are preserved. Conflicting seed keys keep the earliest ID canonical and rename later keys with a deterministic `__legacy_demo__<id>:` prefix. They remain explicitly tagged for cleanup; no distinct notes are merged. The migration is irreversible because removed ownership cannot be reconstructed. Take a restricted database backup before applying it. Notes without highlights remain independently anchored; combined lists use explicit foreign-key relationships instead of guessing by identical text.
