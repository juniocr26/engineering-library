# Trust boundaries — Cofre Paciente

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

PoliticaRequisicaoCofre binds issuer vivabem, audience cofre-paciente and a path-specific scope to SHA-256 of uppercase method + newline + exact path + newline + encrypted body. The Portal counterpart uses the same map and rejects protected claim overrides/redirects. Encryption is selective; do not infer all Mongo fields are encrypted. This policy authenticates the Portal capability; it does not independently prove authorization of each browser actor or stop replay.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
