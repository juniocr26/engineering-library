> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — Criptografia Lib

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: scope -->

## Inspection coverage

Follow-up: both repositories were on `main` with clean working trees. The source README conflict markers were already versioned. Internal guides were reconciled against the implementation; the `tag` branch was inspected read-only and contains no internal documentation. Its runtime source, Composer manifest and tests match `main`. The earlier release-branch review remains valid for runtime observations, but did not cover the internal documentation now reviewed on `main`.

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No consumer application, operational database, broker or deployment command ran. Library catalog maintenance is separate and reported below.

<!-- reading-section: sources -->

## Source files

- `criptografia-lib/composer.json`
- `criptografia-lib/src/Configuration.php`
- `criptografia-lib/src/Crypto.php`
- `criptografia-lib/tests/CryptoTest.php`
- `criptografia-lib/docs/en/security/envelope-v1.md`
- `criptografia-lib/docs/en/architecture/implementation-map.md`
- `criptografia-lib/docs/en/integrations/integrations.md`

<!-- reading-section: history -->

## Historical reuse and corrections

The historical map supplies the responsibility split and exact-byte custody lesson. Earlier October 11 descriptions of an unauthenticated IV refer to a retired format. Current `src/Crypto.php` authenticates the literal header and IV as well as ciphertext and rejects unmarked legacy envelopes. Preserving a PEM does not make that retired format readable.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/criptografia-lib.md`
- `engineering-library_old/docs/en/interviews/criptografia-lib-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. The earlier review did not run catalog synchronization. Follow-up documentation/catalog checks and synchronization are reported separately in the delivery; no application or cryptographic suite was executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Independent cryptographic review, a legacy migration procedure, key rotation, restore acceptance and verification of installed consumer dependencies remain open. No runtime/security suite ran.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)
