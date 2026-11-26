# Technical FAQ — VivaBem Android

[English](index.md) | [Português brasileiro](../../pt-br/faq/index.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: q001 -->

## Q001 — Does DAL authenticate the user?

No. It verifies the package/certificate relationship with the web origin. Portal authentication and authorization still decide user access, and notification permission/FCM delivery are separate capabilities.

<!-- reading-section: q002 -->

## Q002 — Can a key be regenerated to repair debug signing?

That changes signing identity and can break origin association and installed-app compatibility. Gradle deliberately requires the existing fixed debug identity; recover authorized original material and verify certificate association instead of silently replacing it.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Installed-certificate verification, live DAL response, device/browser lifecycle, denied/stale push behavior, signed release and Play publication remain unverified. Token-to-authorization association and full session-specific delivery filtering require further investigation.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
