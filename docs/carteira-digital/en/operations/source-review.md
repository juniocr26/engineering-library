> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — Carteira Digital

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `carteira-digital/composer.json`
- `carteira-digital/routes/api.php`
- `carteira-digital/app/Http/Controllers/TransacaoController.php`
- `carteira-digital/app/Http/Controllers/MercadoPagoWebhookController.php`
- `carteira-digital/app/Services/BalanceReader.php`
- `carteira-digital/app/Services/MercadoPagoEnvironment.php`
- `carteira-digital/app/Services/RuntimeCryptoConfiguration.php`
- `carteira-digital/config/crypto.php`
- `carteira-digital/config/services.php`
- `carteira-digital/database/migrations/2025_08_31_143316_transacao.php`
- `carteira-digital/tests/Feature/BalanceReaderTest.php`

<!-- reading-section: history -->

## Historical reuse and corrections

The historical architecture/interview explain ownership, idempotency identities, uncertain provider outcomes and local transaction limits. Their Stripe/Connect accounts, payout outbox/inbox and refund-lot execution are retired descriptions. Current controllers and migration supersede those mechanisms. Mercado Pago signature reception is foundation only, with 503 instead of an acceptance acknowledgement.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/carteira-digital.md`
- `engineering-library_old/docs/en/interviews/carteira-digital-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Durable Mercado Pago inbox/consumer, financial execution, provider reconciliation, production acceptance, schema upgrade/migration and real MySQL concurrency remain open. The nine-field schema is inspected, not applied here.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)

## Result delivery and operational observation — reviewed 2026-11-10

IMPLEMENTED: `CasoDeUsoComprarAtendimentoSaldo` locks the owner's balance before idempotent lookup and checks owner, amount, type, environment, purpose, appointment and duration. A repeated approved attempt returns without another debit. Insufficient funds rolls back the newly created operation. Debit and `debit_applied` commit together; interrupted execution checks persisted approval before deciding whether to retry. Delivery remains a separate `effects_pending` obligation.

`AdaptadorOrdersMercadoPago::situacao` requires both order and payment `processed/accredited` for approval; `failed/processing_error` stays pending. Refusal requires recognized terminal combinations, not any HTTP error. Result translation checks opaque external reference, configured seller, order identity, BRL/BRA constraints, exact cents, one payment and method/payment identity. A returned payer must agree; an omitted payer is not fabricated. Approved results additionally require exact paid amounts. Submission uses the existing idempotency key, no redirects and bounded timeouts. Recognized 423/429 throttling preserves retry timing; ambiguous responses remain uncertain.

`AdaptadorResultadoCompraPortal` sends the encrypted result to `/api/internal/balance-purchases/results` with an HS256 JWT valid for 60 seconds, scoped and bound to POST/path/body/subject. HTTP success without `persisted=true` raises an unconfirmed-effects error. SQL approval therefore does not prove that Portal notifications or appointment application completed. Operators must retain original transaction/attempt/event identities and inspect outstanding effects rather than create another charge.

`ObservabilidadeReconciliacao` records supported external purchases, excluding synthetic Pix identities. It separates attempt, provider query, retry, credit-start, after-commit credit-confirmation and observed-result events. `credito_iniciado` is explicitly not proof of credited balance. Schema version 1 correlates events to the transaction; owner/amount/provider identifiers are sensitive operational metadata and must not be copied into public examples. Deferred recording runs after MySQL commit when applicable; preparation/storage failures are caught and logged without changing financial processing.

`AdaptadorObservabilidadeReconciliacaoRedis` uses a Lua script with type checks and available ACL preflight. It appends per-transaction events with a sequence, replaces metadata and maintains a per-owner sorted index. Metadata/events/index expire after 604800 seconds (seven days), refreshed by writes; old index entries are pruned. This temporary Cockpit projection is not an immutable financial ledger, settlement proof or a source for reconstructing missing SQL state. No live Redis/ACL/provider test was performed here.

Sources: `app/UseCases/CasoDeUsoComprarAtendimentoSaldo.php`, `app/Adapters/AdaptadorOrdersMercadoPago.php`, `app/Adapters/AdaptadorResultadoCompraPortal.php`, `app/Services/ObservabilidadeReconciliacao.php`, `app/Adapters/AdaptadorObservabilidadeReconciliacaoRedis.php`. Maintenance trigger: changes to statuses, delivery acknowledgement, event schema, retention or retry classification require both language guides and the curated collection to change together.
