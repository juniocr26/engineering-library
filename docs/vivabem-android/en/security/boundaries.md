# Trust boundaries — VivaBem Android

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

Digital Asset Links associates a package and certificate with the web origin; it is not user login. A safe launch URI prevents untrusted-origin entry but does not authorize a domain action. A received push may be stale: reread authorized current state before acting. Denied notifications must not become evidence of logout. No keystore, certificate file, Firebase credential or personal token was opened.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
