# Failure reasoning — Criptografia Lib

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

There is no database or persistent key store in `src/`. Exact PEM bytes participate in HKDF: equivalent RSA keys serialized differently need not derive the same subkeys. No key ID, rotation registry or automatic legacy reader exists. Original keys and envelope-version compatibility must both survive restoration.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Read `composer.json`, then `Configuration::validate`, `Crypto::__construct`, `encrypt` and `decrypt`. In an independently authorized disposable consumer, use an ephemeral synthetic RSA key and roundtrip a string such as `synthetic-message`; mutate the IV, header and tag independently and expect rejection. These are suggested checks, not commands executed here. Coordinate package/version and data-format migration across consumers before deployment.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
