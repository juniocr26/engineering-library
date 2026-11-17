# Current backend suite and verification boundaries

[Contents](../index.md) | [Português brasileiro](../../pt-br/operations/backend-testing.md)

Reviewed and executed 2026-11-10. Audience: maintainers and reviewers. A: current source/test assertions; execution is recorded separately. No tests, fixtures, dependencies, application logic or infrastructure were changed.

<!-- reading-section: harness -->
## Actual harness and isolation

`tests/TestCase.php` creates a minimal Laravel application with in-memory SQLite and validation/translation/FormRequest providers, synthetic JWT configuration and a mocked logger/view. It blocks stray Laravel HTTP requests and resets Carbon, JWT timestamp/leeway, models and facades. Mongo repositories, encryption and remote dependencies are substituted in these scenarios. It is not the removed tests/TesteIsolado.php harness.

`phpunit.xml` bootstraps vendor/autoload.php and discovers Unit/Feature directories. Folder names do not imply every case traverses the HTTP kernel. Tests use PHPUnit 11.5.56/Mockery and existing local dependencies.

<!-- reading-section: scenarios -->
## Existing test modules

| File | Contract asserted |
| --- | --- |
| `tests/Unit/IdentificadoresCartoesTest.php` | Mongo map-key rejection, bounded diagnostic paths and minimal card-reference/environment validation |
| `tests/Unit/ProcessadorMensagemRemocaoGoogleMeetTest.php` | ACK only on completion, reject only with persisted pending evidence, malformed input and dependency failures |
| `tests/Unit/RetencaoAvaliacoesTest.php` | Accounted flag, strict date/cutoff boundaries and invalid date rejection |
| `tests/Feature/AutorizacaoLinksApiTest.php` | Real local router/middleware/controller/use-case dispatch with mocked crypto/repository; denial before decrypt for invalid claims/body/query |
| `tests/Feature/CartoesTest.php` | Legacy token redaction, incomplete/unreadable lists and owner/observed-value compare/delete |
| `tests/Feature/AvaliacoesTest.php` | Integer stars 1–5, duplicate result, normalized professional IDs and aggregate responses |
| `tests/Feature/RecuperacaoLinksTest.php` | Absent deletion idempotency and continued recovery after one identity fails |

<!-- reading-section: execution -->
## Executed result

From this repository root:

```sh
composer test
```

Composer resolves to `php vendor/bin/phpunit --do-not-cache-result`. Exit 0 on PHP 8.3.27 / PHPUnit 11.5.56: **58 tests, 156 assertions**, all passed. No external service, production credential or deployed database was used. No coverage percentage was measured.

<!-- reading-section: limits -->
## Gaps, history and maintenance

Deployed MongoDB indexes/atomicity, production card-provider deletion, full debit-controller behavior, broker retry/DLQ transport and actual conferencing cleanup remain unverified. The message processor test validates its returned action, not a live broker acknowledgement.

The earlier 21/52 report and its three named test files are obsolete as a current inventory. Keep historical outcomes attributed to that earlier execution.

Sources: composer.json, phpunit.xml, tests/TestCase.php and each test file above. Recheck both languages and the Engineering Library counterpart after test names, harness, domain contracts or execution commands change. A passing suite is not provider homologation or documentation completeness. New tests are outside this documentation task.
