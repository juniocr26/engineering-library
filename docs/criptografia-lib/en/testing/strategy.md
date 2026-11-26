# Cryptographic verification and compatibility limits

[Contents](../index.md) | [Português brasileiro](../../pt-br/testing/strategy.md)

Reviewed/executed 2026-11-10. Audience: package maintainers and consumer reviewers. Source API is CriptoLib\Crypto with Configuration::validate, encrypt and decrypt; no code or test was changed.

<!-- reading-section: contract -->
## Contract under verification

The constructor accepts the exact algorithm label RS256 and a valid RSA private PEM, but encrypts data with AES-256-CBC plus HMAC-SHA256, not RSA encryption. HKDF derives separate keys from untouched PEM bytes. The envelope is CLIB:1:A256CBC:HS256: followed by canonical base64 of IV/ciphertext/tag. Decrypt authenticates header/body before OpenSSL decryption and rejects legacy, unsupported, malformed or modified input. Reformatting even equivalent PEM bytes changes derived keys; validation-copy repair does not normalize the original input.

`tests/security-cases.php` is shared by standalone tests/runtime.php and PHPUnit tests/CryptoTest.php. It uses ephemeral synthetic keys and an independent reference implementation; assertions cover roundtrips, randomization, framing, canonical encoding, header/version/IV/ciphertext/tag tampering, wrong keys, truncation, legacy rejection and configuration. A test-only OpenSSL wrapper checks that rejected cases do not reach decryption. This is regression evidence, not formal cryptographic certification or consumer deployment validation.

<!-- reading-section: execution -->
## Executed result

From repository root:

```sh
php tests/runtime.php
```

Exit 0, **292 security assertions passed** on PHP 8.3.27. No application bootstrap, operational keys, stored ciphertext, database or Docker was used. The standalone command does not require PHPUnit. Composer defines test as phpunit, but that PHPUnit command was not executed in this continuation; do not conflate the two results.

<!-- reading-section: history -->
## Historical evidence retained

The 2026-10-22 report recorded 288 assertions. The 2026-10-23 report recorded 292 and one PHPUnit test/292 assertions, including host/container execution and a synthetic historical MAC-omission reproduction. Those remain dated outcomes, not executions repeated here. Earlier documentation's 2026-11-04 host report also recorded 292. Current standalone verification independently reconfirmed the same count.

<!-- reading-section: limits -->
## Limits and maintenance

PHP >=8.1/OpenSSL is declared, but this invocation verified only PHP 8.3.27. No PHP 8.1 matrix, production migration, consumer suite, key rotation, live store or cross-language reader was executed. No replay protection, authorization or password hashing is provided by reversible encryption. Apps must coordinate supported envelope version, original PEM custody and failure handling; a passing package suite cannot prove installed consumer versions match this checkout.

Evidence: composer.json, src/Configuration.php, src/Crypto.php, tests/runtime.php, tests/security-cases.php, tests/CryptoTest.php. Recheck both languages and collection after framing, KDF, accepted PEM, errors or tests change. Preserve security history; do not change algorithms/tests to make documentation validation pass.
