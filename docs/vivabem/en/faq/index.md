# Technical FAQ — vivabem

2026-11-04. Static review of current contracts; no provider call.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — How are purchases and balance reads separated?

LeitorSaldo signs an owner/body/path-bound read to Carteira /api/get_saldo and validates the encrypted decimal-string response. Purchase controllers delegate through the current financial adapter/client and Use Cases. The retired generic unavailable shell is not the current purchase contract. A successful balance read does not approve a purchase.

<!-- reading-section: q002 -->

## Q002 — Does any app heartbeat renew the 60-day authorization?

SessaoAutenticacaoRedis separates qualifying activity from passive presence, Hub and video heartbeats. Authorization, persistent eligibility, cookie lifetime and reachable notification transport are separate lifecycles. The Android source marker alone is not authentication.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Complete appointment transitions, live videoconferencing/FCM, queue recovery, accessibility, concurrent database behavior and production startup/restore were not executed. Callback routes are implemented with their own scoped JWT validation; route presence does not prove delivery.

## Does a saved card or signed webhook prove payment completion?

No. Tokenization, customer association, encrypted storage, provider approval, SQL financial effect and Portal delivery are separate outcomes. Local Pix simulation also differs from provider confirmation.

[Integration / Integração](../integrations/mercado-pago.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../vivabem/docs/en/architecture/current-implementation.md).
