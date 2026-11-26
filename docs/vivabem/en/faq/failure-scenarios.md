# Failure reasoning — VivaBem

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `f0b884ca536a26996d40bf4187981d8c7506d0d7`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

SQL identity/appointment state, Redis authentication, Cofre documents and wallet balances have separate commit authorities. Opening a read projection is not a distributed transaction or provider reconciliation. Dashboard batching bounds query batches but does not prove constant memory for the final collected result. SessaoAutenticacaoRedis stores a hashed credential reference and a password fingerprint; current persistent policy uses rolling 60-day inactivity. Cookie transport lifetime is distinct. Passive presence, Hub and video heartbeats are excluded from qualifying renewal.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Start the reading path with CasoDeUsoLeituraPainel, then dedicated LeitorSaldo and the two peer clients, followed by the authentication session and signer. Trace wallet/Cofre counterparts before diagnosing cross-service failures. For future isolated tests, use synthetic users and HTTP/Redis doubles, test a missed notice followed by authorized reread, invalid encrypted response, body-bound denial, upstream timeout and context revocation. A timeout can leave a remote effect uncertain; do not infer rollback from a missing response.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
