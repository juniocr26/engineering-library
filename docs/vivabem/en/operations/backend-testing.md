# Portal tests: current suite and verification limits

> Current loading/test consolidation: see the final phase 4 section below. Runner availability and 54/190 counts in the preserved 2026-11-10 record are historical.

[Contents](../index.md) | [Português brasileiro](../../pt-br/operations/backend-testing.md)

Reviewed/executed 2026-11-10 at revision `d412cc7`. Audience: maintainers and reviewers. This replaces the outdated current-suite description of 2026-11-04; older counts remain historical rather than new evidence. No test, runner, fixture, dependency or application code was changed.

<!-- reading-section: harness -->
## Actual harness and isolation

`phpunit.xml` bootstraps `vendor/autoload.php` and discovers `tests/Unit` and `tests/Feature`. The local `vendor/bin/phpunit` now exists; borrowing another repository's runner is unnecessary. `tests/TestCase.php` extends PHPUnit directly, creates an in-memory Laravel application/container, configures SQLite `:memory:`, registers database/hashing providers, provides a mocked view factory/logger and calls `Http::preventStrayRequests`.

It does not boot the full Portal `bootstrap/app.php` or product providers. It is not `tests/TesteIsolado.php`, which is absent. SQLite schema/data writes inside these tests are temporary memory state, not migrations against a deployed database. Laravel HTTP prevention covers that facade; it is not an operating-system sandbox against every possible transport. This review inspected the existing cases before running them.

<!-- reading-section: coverage -->
## Existing contract coverage

| Existing file | Assertions and boundary |
| --- | --- |
| `tests/Unit/AutenticacaoTest.php` | Current/legacy password verification and rehash; missing secret fails closed; credential serialization exclusion |
| `tests/Unit/AgendaFinanceiraTest.php` | Participation-based final status/refund; settled values; temporal boundary and emergency rating eligibility |
| `tests/Unit/ConflitosAgendaTest.php` | Both participants, overlapping/open interval boundaries, excluded appointment, relevant statuses using in-memory SQLite |
| `tests/Unit/ValidacaoDisponibilidadeTest.php` | Pix syntax and availability without authorization/during consultation |
| `tests/Feature/LoginTest.php` | Invalid password, activation, web/remember/Android paths and allowed destination; mocked auth transport |
| `tests/Feature/CadastroPerfisTest.php` | Profile skipped on user failure; failed activation email does not undo successful registration |
| `tests/Feature/NotificacoesTest.php` | After-commit dispatch, rollback, enqueue failure, duplicate reservation and transient job retry |
| `tests/Feature/RegistroPushTest.php` | Registration update/removal ownership, Android downgrade rejection and removed user |
| `tests/Feature/VideoconferenciaTest.php` | Participant, state and five-minute opening boundary with mocked Jitsi |

Names such as Feature do not establish a complete HTTP kernel/browser test. Several cases invoke domain methods directly. The suite does not certify Redis session authorization, complete payment callbacks, MySQL locking, Cockpit routes, broker/FCM delivery or Jitsi operation. Old links to `DecisaoPushTest.php`, `SituacaoFinanceiraAtendimentoTest.php` and `TitularidadeAtendimentoTest.php` were replaced by the actual current file map.

<!-- reading-section: execution -->
## Executed verification

From the Portal repository root:

```sh
composer test
```

`composer.json` resolves this to `php vendor/bin/phpunit --do-not-cache-result`. Actual exit status: **0**. Runtime: PHP 8.3.27, PHPUnit 11.5.56. Result: **54 tests, 190 assertions**, all passed on 2026-11-10. Reported runner time 0.262 seconds, memory 32 MiB; these are invocation observations, not an application benchmark. No coverage percentage was measured.

This used preexisting dependencies, synthetic inputs, in-memory SQLite and existing doubles. No provider call, real financial operation, scheduler, queue consumer or production database was started. Passing results do not certify unsupported platform versions or untested branches.

<!-- reading-section: maintenance -->
## Maintenance and remaining checks

When source/test names change, update both languages and the Engineering Library representation together. Record new executions with date/runtime/counts; never inherit a historical pass as a current result. New automated tests require separate authorization and are outside this documentation task.

Next verification boundaries are application integration and browser/operational checks in an explicitly isolated environment. They were not performed here and should not be replaced by issuing administrative Cockpit or financial requests to a live installation. Source evidence: `composer.json`, `phpunit.xml`, `tests/TestCase.php` and the nine case files above. The [Cockpit chapter](technical-cockpit.md) records its separate operational risks.

Re-executed during ecosystem reconciliation on 2026-11-10: `composer test`, exit 0, 54 tests / 190 assertions, PHP 8.3.27 / PHPUnit 11.5.56, 0.306 seconds. This is independent of the earlier run above. Purchase orchestration remains outside this suite’s complete integration coverage.


## Reactive interface testing strategy

Phase 4 documentation review, 2026-11-12. See [shared loading architecture](../architecture/shared-loading.md). Earlier 54/190 results and local-runner availability above are historical observations from 2026-11-10. The current inspected checkout lacks the local PHPUnit executable. Do not infer present reproducibility from that older paragraph.

### Layers and assertions

| Layer | Useful scenarios and expected outcomes | Boundary |
| --- | --- | --- |
| Blade rendering | Default/null/blank/custom text; escaping; props; class visibility versus Alpine attributes; modal opt-in | Confirms generated HTML, not expression execution or focus |
| State-controller isolation | Matching attempt/transaction; invalid retry/max; duplicate, regressing and late progress; ambiguous result | Synthetic events do not prove server delivery or settlement |
| Browser + real Alpine | Visible fallback and static/reactive messages; hidden updates/reopen; same image node; independent instances | DOM assertions are stronger than string assertions but need real page coverage separately |
| HTTP ownership integration | Two/three requests finish in any order; success/error/abort; two tables share one indicator; destroy/reinitialize; Pix form cleanup | Verify pending work remains visible and release is idempotent; no production requests required |
| Isolated Socket.IO transport | Object/string envelopes; invalid JSON; context mismatch; retries; duplicate/out-of-order input; reconnect and repeated remount | Compatible endpoint validates client/bridge/store/DOM, not production Hub authentication |
| Focus/layout | Focus only after actual visibility; generic instance leaves keyboard alone; blocking Tab/Escape; cleanup; short/long text and responsive themes | Physical screen reader and other browser engines remain separate |
| Financial frontend | Card, Pix, appointment contexts, refund and receipt synthetic results; delayed/duplicated events and unconfirmed outcomes | Never assert success solely because an indicator closed |
| Build/regression | Asset manifest resolves generated files; existing backend suites remain green | Build success is neither browser acceptance nor distributed integration |

Use controlled synthetic fixtures with no customer records or credentials. Keep real Alpine/controllers/bridge logic under test; mock HTTP/business dependencies at their boundaries rather than replacing the logic being asserted. For payments, simulate preparation, sending, pending, rejection and unknown outcomes separately. An HTTP 5xx or lost response can mean uncertainty; it must not manufacture approval or encourage duplicate payment. A QR state alone is insufficient to establish a purchase result. Distinguish complete submission scenarios from merely instantiating an appointment controller.

A useful ownership sequence is: acquire A, acquire B, finish A, assert still visible, finish B, assert initial state restored, release A again, assert unchanged. Repeat with error, abort, reversed order, a third owner and an initially visible overlay. Destroy while pending and remount a new instance; late callbacks from the old instance must not hide or draw into the new one. Direct class manipulation outside the ownership helper is outside those guarantees.

For Socket.IO, use a loopback-only compatible endpoint with synthetic identifiers and controlled disconnects. Observe real transport frames and the final visible text, not only dispatched browser events. Check exactly one owned handler after each of several remounts, no old callbacks after destroy, and no business-listener growth after reconnect. Channel selection on a client is not server authorization. Do not claim polling/upgrade coverage from a WebSocket-only fixture or label a minimal Engine.IO-compatible endpoint the actual Hub.

### Evidence matrix from the loading consolidation

The final temporary Chromium JSONs and PHPUnit JUnit outputs were inspected during this documentation review. No application tests or financial operations were rerun. Corrective records describe D01–D06 as fixed, consistent with current source. The original final report is absent in the checkout; its retained temporary corrective record and outputs provide partial provenance, not a permanently archived report.

| Area | Scenario | Test source | Evidence level | Last verified result | Limitations |
| --- | --- | --- | --- | --- | --- |
| Shared component/default/props | Omitted/null/blank/custom, status region, escaping, opt-in and removed wrapper | Existing focused PHPUnit component suite | Permanent declarative test; prior output inspected | 12 tests/55 assertions passed | No Alpine execution in PHP |
| Alpine/custom/class visibility | Real message changes, missing simple identifier, image identity, reopen, multiple instances | Temporary Chromium harness | Component/browser isolation | Passed within 544 | Not a versioned browser suite |
| Concurrent operations/DataTables | Overlap, errors, abort, out-of-order, multiple tables, destroy/reinit | Temporary targeted harness | Real controller/library with controlled HTTP | 19/19 targeted checks | Not arbitrary DOM mutation coordination |
| Pix form lifecycle | Pending abort/destroy, stale state, other owner preserved | Temporary targeted harness | Real controller with synthetic HTTP | 40/40 targeted checks | No operational form write |
| Retry/Socket.IO | Sequence 1–5; parser, context, duplicates, regression, reconnect/remount and DOM | Temporary compatible transport harness | Real client/bridge/state/DOM | 41/41 Socket.IO checks, included in total | No real Hub/Wallet auth or financial provider |
| Focus/accessibility | Reopen, opt-in, keyboard and cleanup | Temporary focused browser harness + declarative PHP | Browser isolation | 48/48 targeted checks | No physical screen-reader certification |
| Long text/responsive | Four viewport widths, two themes, short/medium/long and scroll | Temporary layout harness | Chromium geometry/DOM | 48/48 targeted checks | Other engines unverified |
| Financial frontend | Card/Pix, appointment contexts, refunds/receipts, uncertain outcome and premature-success prevention | Temporary synthetic scenarios | Controller/component isolation | Passed within 544 | Complete distributed submissions not certified |
| Twelve generic surfaces | Transaction history, table/calendar history, listing, three auth variants, four profile variants, Pix key form | Temporary component/integration isolation | Individually exercised surfaces | Passed | Not full authenticated-page acceptance; depth varies |
| Chromium regression | Original scenarios plus targeted D01–D06 checks | Twelve temporary result sets | Earlier execution outputs inspected | 544/544; zero unexpected global exceptions | Includes 41 Socket.IO checks, not 585; temporary artifacts may disappear |
| Full PHPUnit | Current existing suites including focused component tests | Final JUnit output | Earlier automated regression | 127 tests/957 assertions; zero failures/errors/skips | Focused 12/55 already included; borrowed runner |
| Vite/assets | Container build and manifest validation | Corrective record and retained manifest | Reported pass with artifact | Passed in corrective record | Full raw build logs absent; not rerun here |

D01's targeted message checks passed 26/26 and D05's targeted remount checks passed 28/28; these are portions of the 544 total, not additional test suites. Five was a synthetic retry sequence, not a universal deployment maximum. No coverage percentage is inferred from assertion counts.

### Reproduction and evidence limits

The existing PHPUnit setup uses a minimal Laravel container, SQLite in memory, HTTP prevention and mocks, rather than the complete production kernel. Standard execution requires the project's development PHPUnit/Mockery dependencies, correct development autoloading and compatible PHP/extensions. When available, use the project's documented composer test entry point and a PHPUnit filter for the focused component suite. The current checkout does not supply that runner; no dependencies were installed for documentation.

The earlier final run reused an existing neighboring development runner (PHP 8.3.27, PHPUnit 11.5.56, Mockery 1.6.15). Its temporary bootstrap explicitly prioritized the target project's test namespace so the neighboring TestCase could not be loaded accidentally. This is a local workaround, not a universally available command; no machine-specific bootstrap or path is published here. Restoring standard project dev dependencies is the prerequisite for a portable invocation.

The frontend provides build/dev commands, not a permanent command reproducing all 544 browser checks. Temporary browser verification required Chromium/Playwright, real rendered components, bundled modules, controlled HTTP and an isolated compatible transport endpoint. Those artifacts were not promoted to a maintained suite. The Vite build used existing Linux-container dependencies and temporary output followed by asset-manifest validation; host-native modules should not substitute for the container's native build dependencies.

The owner separately confirmed functionality in a real environment. No date, devices, individual transactions or screenshots were supplied. This manual acceptance does not erase missing full-page authenticated coverage, actual provider integration, real Hub authentication, cross-service end-to-end reconciliation, genuine BFCache, other browser engines or physical screen-reader checks. These are evidence limitations, not reopened defects.

Permanent browser tests for reactive DOM, HTTP ownership and socket lifecycle would improve reproducibility. They remain a recommendation requiring separate authorization; this documentation phase changed no tests, fixtures, dependencies or reader UI. Green unit tests cannot prove a distributed financial system completed its external effects.
