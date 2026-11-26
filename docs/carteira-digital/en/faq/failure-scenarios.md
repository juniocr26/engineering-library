# Failure reasoning — Carteira Digital

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

The transacao migration defines nine fields: oid_transacao (36-character primary key with UUID default), oid_usuario, globally unique required chave_idempotencia, tipo_transacao, unsigned integer valor_centavos, moeda default brl, situacao_transacao, data_transacao and nullable JSON metadados. The user/date index supports lookup, not ownership. Consolidated fresh-schema migrations are not an in-place upgrade for an existing deployment. A unique key prevents duplicate stored identities but does not implement provider execution or reconciliation.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Trace the dedicated Portal balance client, wallet middleware and reader before diagnosing dashboard balances. Preserve the distinction between exists=false and failure. For future isolated acceptance, create a disposable schema and synthetic owner; check an existing balance, absent balance, duplicate row, wrong sub/hash, malformed envelope and unavailable database. Do not replay old provider queues, run migrations on existing data or start financial workers from historical instructions.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
