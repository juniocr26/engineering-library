# Technical FAQ — Criptografia Lib

[English](index.md) | [Português brasileiro](../../pt-br/faq/index.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: q001 -->

## Q001 — Does RS256 encrypt the data?

No. RSA PEM validity is checked, but AES-256-CBC encrypts the payload and HMAC-SHA256 authenticates it. Confusing that label with asymmetric payload encryption hides the shared-secret custody boundary.

<!-- reading-section: q002 -->

## Q002 — Can equivalent PEM formatting be substituted?

Not safely: HKDF consumes exact input bytes. Validation reframing never changes those derivation bytes. Preserve the original representation and test restore with the actual format/version.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Independent cryptographic review, a legacy migration procedure, key rotation, restore acceptance and verification of installed consumer dependencies remain open. No runtime/security suite ran.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
