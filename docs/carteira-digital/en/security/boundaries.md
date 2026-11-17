# Trust boundaries — Carteira Digital

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

CasoDeUsoConsultarSaldo requires sub equal to the requested owner, issuer vivabem, audience carteira-digital, scope wallet:balance:read and a SHA-256 request_hash over POST, exact path and encrypted body. Generic service credentials alone are insufficient for that read. Failed binding returns 403, malformed encrypted input 422, ambiguous/infrastructure failure 503. Neither authentication nor webhook signature validation proves a financial effect. Never turn an upstream outage into a zero balance.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
