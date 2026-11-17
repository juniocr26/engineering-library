# Failure reasoning — Cofre Paciente

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

RepositorioCartoes stores user-keyed maps, validates dynamic map identifiers and uses Mongo point updates. deleteObserved compares the exact observed string/type with simple collation before $unset, returning whether one item changed. LeitorFinanceiroArmazenado decodes current authenticated envelopes and validates card JSON, retaining unreadable entries as null and returning complete=false. Repository/configuration failures propagate instead of being disguised as a complete empty list. Mongo single-document updates do not create a transaction with Portal SQL or remote services.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Study Portal ExternalPosterCofrePaciente and both PoliticaRequisicaoCofre files together. In a separately authorized isolated fixture, test a valid synthetic request, body/path substitution, expired token, exact replay and unreadable stored item. For deletion, retain the observed value and detect changed storage rather than blindly replacing an entire map. Remote conference cleanup and local reference removal have distinct outcomes; inspect the existing queue runbook before any replay.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
