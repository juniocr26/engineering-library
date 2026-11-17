# Trust boundaries — Criptografia Lib

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

RS256 is a configuration label/validation requirement here; payloads are not RSA-encrypted JWTs. The HMAC covers the IV in the current format. Authentication of bytes does not establish actor identity, record ownership, freshness or replay prevention. Never normalize stored key bytes or generate a replacement key as a repair for unreadable data.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
