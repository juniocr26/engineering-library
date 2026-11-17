# Technical FAQ — cofre-paciente

2026-11-04. Static review of current contracts; no provider call.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — Does a valid Cofre token prevent replay?

No. PoliticaRequisicaoCofre binds method/path/body and limits lifetime without a consumed-nonce store. It does not provide exactly-once mutation. Debit additionally checks delegated sub against the decrypted owner; the credit base Use Case does not have that same additional check.

<!-- reading-section: q002 -->

## Q002 — Why preserve an unreadable item?

Rejected stored envelopes differ from absence. LeitorFinanceiroArmazenado reports item identity and incomplete results; repository/configuration failures are separate. Deletion requires an observed hash and exact-value comparison. Debit has a separate rejected-envelope branch; do not assume identical manual credit/debit deletion.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Real Mongo concurrency, deployed indexes, complete rating lifecycle, queue recovery, backup restoration and end-to-end owner authorization remain unverified here. Production debit deletion/provider confirmation is implemented but was not exercised. No live Mongo, broker or provider call ran.

## Does a saved card or signed webhook prove payment completion?

No. Tokenization, customer association, encrypted storage, provider approval, SQL financial effect and Portal delivery are separate outcomes. Local Pix simulation also differs from provider confirmation.

[Integration / Integração](../integrations/saved-cards.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../cofre-paciente/docs/en/architecture/current-implementation.md).
