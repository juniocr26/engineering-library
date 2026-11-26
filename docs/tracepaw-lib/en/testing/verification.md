# Existing tests and verification evidence

[Contents](../index.md) | [Português brasileiro](../../pt-br/testing/verification.md)

Reviewed and executed 2026-11-10. Audience: reviewers and maintainers. Scope: existing library suite and documentation checks. This chapter records observed results, not historical reports or production certification. No test, fixture, runner, application code or dependency was created or modified.

<!-- reading-section: suite -->
## Existing suite and isolation

`composer.json` defines `test: phpunit`; `phpunit.xml` bootstraps `tests/bootstrap.php`, discovers `tests/`, and fails on warnings/risky tests. Bootstrap loads Composer and the existing namespaced filesystem-operation hooks. `tests/Suporte/TesteIsolado.php` allocates random private temporary directories and removes only its test-owned tree. Existing `OperacoesArquivo.php` hooks simulate failures; real-process tests use `proc_open` and the existing `tests/Suporte/processo.php` against those temporary directories. They do not target application logs or databases.

| Existing test area | Contracts asserted |
| --- | --- |
| `tests/Dominio/CampoContextoTest.php` | Strict scalar typing, bounds, allowed lists, shorthand |
| `tests/Dominio/TagsTest.php` | Normalization, controlled dimensions, rejected collisions/values |
| `tests/Dominio/EventoTest.php` | Full schema, UTC conversion, optional-field omission |
| `tests/Aplicacao/CatalogoTest.php` | Extensible catalog, invalid definitions/identity, unknown codes |
| `tests/Aplicacao/RegistradorTest.php` | UUIDs, identity ownership, protected fallback, contradictory input |
| `tests/Aplicacao/ContextoTest.php` | Sensitive/unknown removal, UTF-8, scalar limits, absent/null/zero/false |
| `tests/Aplicacao/DiagnosticoTest.php` | Redaction, no trace arguments, relative paths, bounded causes/frames |
| `tests/Aplicacao/RuidoTest.php` | Eligibility, first write, thresholds, correlation, failed flush, bounded groups |
| `tests/Infraestrutura/SerializadorTest.php` | JSON Lines, byte limit, nonfinite errors |
| `tests/Infraestrutura/PsrTest.php` | All severity mappings, structured context, failure chaining |
| `tests/Infraestrutura/ArquivoDiarioTest.php` | UTC rotation, permissions, edge checks, links, partial writes/restoration |
| `tests/Integracao/ContratoRegistroTest.php` | Registrar-to-file recovery summary and private-message exclusion |
| `tests/Integracao/ProcessosTest.php` | Four cooperating writers/300 events, lock blocking, abrupt termination |

Process tests assert scoped concurrency behavior, not measured throughput. Abrupt termination covers an in-memory pending summary, not every possible crash point or power loss.

<!-- reading-section: execution -->
## Executed command and result

Working directory: library root, with preexisting `vendor/`. Host runtime was used for this standalone PHP package; no container definition exists in the inspected library. The command disables result-cache writes:

```sh
composer test -- --do-not-cache-result
```

Actual result: exit 0; PHP 8.3.27; PHPUnit 11.5.57; **210 tests, 1323 assertions**, all passed, 2026-11-10. Reported suite time 1.896 seconds and memory 12 MB are runner observations for this invocation, not application performance claims. No skipped tests were reported. No coverage measurement was requested or produced. Passing on PHP 8.3 does not certify every version admitted by `^8.2` or every filesystem/platform.

The installation guide's complete executable PHP example passed `php -l` and actual execution in an owned disposable directory on 2026-11-10: one JSON Lines record, matching UUID, schema `1.1`, event code and numeric context were verified. English/Portuguese example code was identical. The reliability chapter’s opt-in aggregation example also passed PHP lint and execution: first ID present, repeated ID null, two records, count `1`, reason `explicit_flush` and latest context verified; both languages use identical code. API declaration fences are signatures, not standalone runnable programs. Exact documentation-check commands/results belong to the task delivery report; static structural parity does not replace bilingual semantic review.

<!-- reading-section: limitations -->
## Validation boundaries and maintenance

Not executed: private registry installation, Laravel binding, Datadog delivery, live applications, production filesystem/collector checks, backup/restore, release compatibility matrix, load benchmarks or frontend visual review. Engineering Library's Docker socket was unavailable in this session; no service was created, started or reconfigured. Catalog synchronization is a database mutation and was not run.

Full `tools/check_catalog.py` includes a historical fixed project inventory/provenance manifest. A new collection can therefore cause an inventory mismatch until provenance policy is deliberately reconciled. This task does not regenerate historical provenance or snapshots to silence that check. Scoped in-memory checks can validate new Markdown paths, anchors, bilingual section identities and reachability separately; the final report must identify which were executed.

Maintainers should rerun the existing suite after library contract changes and record date/runtime/result without presenting old outcomes as new. Update both languages when test names, scope, isolation or command changes. New tests or test scaffolding require separate authorization; this documentation creates none. Sources: `composer.json`, `phpunit.xml`, existing `tests/` files listed above and support helpers. Review approval remains with the owner/designated technical reviewer.

## Current evidence — 2026-11-11

Local library suite at `4b99743`: `php vendor/bin/phpunit --do-not-cache-result`, exit 0, PHP 8.3.27, PHPUnit 11.5.57, **210 tests, 1323 assertions**. This does not certify publication, deployment or production integration. No test was changed during this documentation maintenance.
