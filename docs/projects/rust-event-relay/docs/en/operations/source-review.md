# Provenance and limits

- Repository: `rust-event-relay`
- Workspace: `rust-event-relay/`
- Git revision: `a1e0fa1513a8cbdf362f06f5cf1bdd906eb2430c`
- Remote (observed, not fetched): `git@github.com:juniocr26/rust-event-relay.git`
- Review: 2026-10-18, static/selective.

READMEs and maintained documentation in `docs/en/` and `docs/pt-BR/` were read and imported preserving filenames and ADRs. Existing Library interviews were relocated with compatibility entries at old paths. Relative links were adapted to cataloged copies or local workspace sources; explanations are local, but code links require sibling repositories. Restricted links are rendered as non-navigation text. No remote URL was checked.

## Inspected implementation sources

- [backend/src/application.rs](../../../../../../../rust-event-relay/backend/src/application.rs)
- [backend/src/persistence/mod.rs](../../../../../../../rust-event-relay/backend/src/persistence/mod.rs)
- [backend/src/infrastructure/postgres/mod.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/postgres/mod.rs)
- [backend/src/bin/relay.rs](../../../../../../../rust-event-relay/backend/src/bin/relay.rs)
- [backend/src/bin/consumer.rs](../../../../../../../rust-event-relay/backend/src/bin/consumer.rs)
- [backend/src/bin/demo.rs](../../../../../../../rust-event-relay/backend/src/bin/demo.rs)

## Limits

Selective static inspection, not a complete code audit or application/test execution. Earlier results belong to their source revision/date, not this import. Path parity does not prove translation quality. Undocumented motivations and production readiness were not inferred. Milestones describe different and sometimes conflicting states: start with application-scenarios and milestone-6-3 and treat earlier entries as history. Services, measurements and rollout were not confirmed in this task.

[Import mapping and hashes](../../../../../catalog-provenance.json).
