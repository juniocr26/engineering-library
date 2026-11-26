# Technical FAQ — carteira-digital

2026-11-04. Static review of current contracts; no provider call.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — Does webhook signature verification credit a balance?

Signature verification authenticates ingress. CasoDeUsoProcessarNotificacaoCompra retrieves authenticated Orders state and validates correlation before financial effects. A supported notification may return accepted=true/processed=true, while processing failures can still return 503. Neither signature nor acceptance alone proves an approved payment or a committed balance credit.

<!-- reading-section: q002 -->

## Q002 — Why does a missing balance differ from an unavailable one?

An absent owner balance is an explicit zero/exists=false read without insertion. Duplicate rows, invalid delegation, cryptographic failure or database failure must not become zero. The unique-owner migration rejects duplicates rather than combining balances; deployed migration status was not checked.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Live provider approval, debit homologation, real SQL concurrency, full broker recovery and production acceptance remain unverified in this task. External purchases and reconciliation have source implementations; a separate durable webhook inbox must not be invented from that fact.

## Does a saved card or signed webhook prove payment completion?

No. Tokenization, customer association, encrypted storage, provider approval, SQL financial effect and Portal delivery are separate outcomes. Local Pix simulation also differs from provider confirmation.

[Integration / Integração](../integrations/mercado-pago.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../carteira-digital/docs/en/architecture/current-implementation.md).
