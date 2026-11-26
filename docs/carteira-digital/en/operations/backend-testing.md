# Current backend suite and verification boundaries

[Contents](../index.md) | [Português brasileiro](../../pt-br/operations/backend-testing.md)

Reviewed and executed 2026-11-10. Audience: maintainers and reviewers. A: current source/test assertions; execution is recorded separately. No tests, fixtures, dependencies, application logic or infrastructure were changed.

<!-- reading-section: harness -->
## Actual harness and isolation

`tests/TestCase.php` creates a minimal Laravel container, registers database/hash/cache/validation providers, uses an array cache and configures a connection named mysql backed by SQLite :memory:. It creates synthetic transacao/saldo schemas; it does not boot application providers or production migrations. Laravel HTTP stray requests are prevented; external operations are substituted where exercised. This is not MySQL lock/concurrency validation or an operating-system network sandbox.

`phpunit.xml` bootstraps vendor/autoload.php and discovers Unit/Feature directories. Folder names do not imply every case traverses the HTTP kernel. Tests use PHPUnit 11.5.56/Mockery and existing local dependencies.

<!-- reading-section: scenarios -->
## Existing test modules

| File | Contract asserted |
| --- | --- |
| `tests/Unit/SegurancaFinanceiraTest.php` | Strict decimal-to-cents conversion, rejection of ambiguous amounts, sanitized provider failure classification |
| `tests/Unit/ResultadoOperacaoTest.php` | Public outcome gated by effects_pending; owner, destination and emergency identity rejection |
| `tests/Feature/CompraAtendimentoSaldoTest.php` | One debit for repeated attempt, conflicting attempt rejection and insufficient-balance rollback |
| `tests/Feature/ConclusaoFinanceiraTest.php` | Single credit, late refusal protection, uncertain exhaustion, late conversion to balance and payout breakdown |
| `tests/Feature/RecuperacaoFinanceiraTest.php` | Old redelivery ACK, provider wait without spending a retry, reservation before reconciliation, exhaustion and final-attempt idempotency |
| `tests/Feature/ApiFinanceiraTest.php` | Route/middleware/controller status read with signed claims, owner/environment/body binding and unknown-field rejection |

<!-- reading-section: execution -->
## Executed result

From this repository root:

```sh
composer test
```

Composer resolves to `php vendor/bin/phpunit --do-not-cache-result`. Exit 0 on PHP 8.3.27 / PHPUnit 11.5.56: **60 tests, 178 assertions**, all passed. No external service, production credential or deployed database was used. No coverage percentage was measured.

<!-- reading-section: limits -->
## Gaps, history and maintenance

Real Orders/Pix responses, provider transport, broker confirmation and full consumer ACK/reject behavior, Redis observations, SQL races and deployed recovery remain unverified. SQLite assertions demonstrate the exercised state transitions, not production isolation levels.

The 2026-11-04 guide reported 55/157 and listed files no longer in this checkout. That report is historical; it is not the current suite map.

Sources: composer.json, phpunit.xml, tests/TestCase.php and each test file above. Recheck both languages and the Engineering Library counterpart after test names, harness, domain contracts or execution commands change. A passing suite is not provider homologation or documentation completeness. New tests are outside this documentation task.
