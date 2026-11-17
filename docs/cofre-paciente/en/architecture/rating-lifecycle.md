# Rating accounting and retention

[Index / Índice](../index.md) · [Evidence / Evidências](../operations/source-review.md)

<!-- reading-section: account -->

## Summary and marker ordering

ServicoCicloVidaAvaliacao::daily takes a cooperative cache lock shared with retention, scans contributions with contabilizado=false, requires integer ratings from 1 to 5 and valid appointment/professional identities, and rechecks the observed detail before updating the summary. It writes summary first and exact detail marker second. Failure after the summary write can duplicate contribution on retry; exceptions and logs preserve that uncertainty. This standalone Mongo design does not guarantee exactly-once accounting across documents.

<!-- reading-section: retention -->

## Retention and transition

Retention selects accounted entries strictly older than January 1 of the current America/Sao_Paulo year, accepting BSON UTCDateTime or validated offset-bearing date strings. Conditional $pull targets the observed entry; failed deletion attempts mark exclusao_pendente for retry and report incomplete cleanup. Explicit per-professional transition requires frozen-source discipline, validates unique appointment contributions, writes the baseline summary and then markers; it is not an automatically safe repair of uncertain historical totals.

<!-- reading-section: index -->

## Index contract and verification

ManutencaoIndiceAvaliacao inspects collection/index metadata and compares exact ordered keys for avaliacoes.psicologo and avaliacoes.estrelas.oid_atendimento, expected name and collation. Unique/sparse/hidden/prepareUnique, partial/TTL/wildcard options are incompatible. Provisioning is separate from inspection and may create an index/collection only according to its flag. No index was inspected or created in a real database here; do not infer query latency or applied schema from source.

## Inspected sources

- `cofre-paciente/app/Services/Avaliacoes/ServicoCicloVidaAvaliacao.php`
- `cofre-paciente/app/Services/Avaliacoes/ManutencaoIndiceAvaliacao.php`
