# File delivery, noise lifecycle and operational recovery

[Contents](../index.md) | [Português brasileiro](../../pt-br/operations/reliability.md)

Reviewed 2026-11-10. Audience: operators and long-running PHP worker maintainers. A: source-inspected behavior; tests are mapped in [verification](../testing/verification.md). Scope: local writer and process-local noise, without production recovery certification. Application operators own permissions, retention, collection and incident decisions.

<!-- reading-section: storage -->
## Exclusive directory and daily JSON Lines files

`Infraestrutura\GravadorArquivoDiario` initializes an exclusive directory and marker `.tracepaw-lib-jsonl-v1` containing `tracepaw-lib/jsonl/1\n`. If marker content is empty, initialization requires the directory to contain only that marker; existing legacy logs are not migrated. A valid initialized marker permits later reuse. Constructor initialization has filesystem effects even before registration, so never use production log directories for a smoke check.

Output is `tracepaw-YYYY-MM-DD.log`, choosing the event timestamp's UTC date, not the host timezone or local São Paulo date. There is no rename-based rotation, retention, compression or shipping implementation. The `tracepaw-` prefix does not install the library in Laravel. New directories request `0700`; marker initialization and new empty daily files use `0600`. Existing directory/nonempty file permissions require operator inspection.

For each append the writer serializes first, verifies directory inode/device identity, rejects unsafe file links/nonregular destinations, opens exclusively or safely reopens the regular file, acquires blocking `flock(LOCK_EX)`, then verifies that opened and named file identities agree. Existing files are checked at the first and final record: newline termination, parseable JSON, accepted schema `1.0/1.1`, string event ID/code/timestamp. This is a boundary check, not a complete schema validator or audit of interior records. The test suite explicitly retains intermediate corruption as a documented limitation.

The writer appends under the same lock, loops on partial writes and calls `fflush` and `fsync`. A write/sync exception triggers truncation to the prior size plus flush/sync; failed restoration raises explicit `FalhaGravacao` requiring inspection. Lock release and close occur in `finally`. Cooperating processes are serialized by file lock; no lock timeout or distributed-filesystem guarantee is implemented. Blocking/sync cost is synchronous and unbenchmarked. Sudden process/host failure is not a transactional exactly-once guarantee.

<!-- reading-section: eligibility -->
## Suppression eligibility and first-failure preservation

Default `PreservarEventos` records everything; `AgregarTransitorios` requests aggregation, but registrar eligibility remains mandatory. All these conditions must hold simultaneously:

- Classification `Transitorio`.
- Severity `Depuracao`, `Informacao`, `Aviso` or `Alerta`.
- Outcome `NovaTentativaAgendada`.
- `acaoNecessaria !== true` and `impacto === null`.
- Nonnull validated correlation ID and no Throwable.

Critical/error events, security/operational incidents, confirmed recovery, unknown outcomes, possible data loss and events needing action are never eligible. The synthetic retry-scheduled event is `Esperado`, so is not suppressible merely because its outcome is `retry_scheduled`.

`AgregadorTransitorios::confirmarPrimeiro` creates a group only after successful first write. First write failure cannot enable suppression. With full group capacity, new groups are not tracked and their events continue to be written; existing tracked groups can still aggregate. The default bounds are 60 seconds, 100 suppressed repetitions and 256 groups; ranges are listed in [configuration](../guides/installation.md).

<!-- reading-section: groups -->
## Group identity, summaries and flush

The group key hashes the structured event without `event_id/timestamp`. By default it includes full sanitized context plus request/correlation identity and other event metadata: changing `attempt` ordinarily creates a different group. Optional `DefinicaoEvento::camposAgrupamento` selects approved context fields for grouping; `null` keeps all, `[]` keeps none. Request/correlation identities still participate. Absent field and explicit nullable null remain different. Selecting fewer context fields improves aggregation but deliberately discards those distinctions from identity; review this choice per event.

For explicit grouping, summary context retains only the latest approved `attempt`, `duration_ms` and `retry_delay_ms` present on the last suppressed event. Without explicit grouping it is empty. Stable context remains inspectable through `first_event_id`; summaries do not copy all original context. Summary `aggregation` fields are `source_event_code`, `first_event_id`, `suppressed_count`, `first_seen`, `last_seen`, monotonic `duration_ms` and `reason`. Duration measures last observed repetition relative to the first, not total outage time until recovery.

Reasons are `threshold`, `interval`, `operation_event` and `explicit_flush`. Expiration uses monotonic `hrtime`, evaluated only during registration/flush activity; there is no timer. Threshold evaluation after counting may emit a summary in a call that returns `null`. Summary has its own UUID/current UTC timestamp. The suppressed count excludes the first individually recorded event; totals must combine first events and counts, not count JSON lines alone.

`descarregarRuido()` flushes all pending groups. Successful summary writes confirm/remove groups; repeated successful flush adds no duplicates in the observed in-memory lifecycle. Failed summaries retain state for retry while the process lives. No destructor/shutdown hook, persistence, cross-process aggregation or replay exists. Abrupt termination can lose pending counts while the first successfully written occurrence survives. Injected aggregator configuration is cloned with groups reset per registrar.

A noneligible event closes pending groups for the same `(project, service, environment, correlation_id)`, not by event code, dependency or request ID. Confirmed recovery/escalation with that correlation therefore flushes relevant groups, but does not prove all dependencies recovered. Correlation scope is an integration decision requiring careful ownership.

<!-- reading-section: example -->
## Synthetic opt-in aggregation example

Run from the library root with installed dependencies. This creates a unique disposable log directory. The catalog deliberately uses no context grouping fields so changing attempt/delay does not split the group; producer/correlation/request identity still participates. It records a scheduled retry assertion without performing any retry.

```php
<?php

declare(strict_types=1);
require getcwd() . '/vendor/autoload.php';

use TracePaw\Aplicacao\{AgregarTransitorios, Catalogo, Configuracao};
use TracePaw\Dominio\{Classificacao, DefinicaoEvento, Resultado, Severidade};
use TracePaw\Infraestrutura\GravadorArquivoDiario;
use TracePaw\Registrador;

$directory = sys_get_temp_dir() . '/synthetic-noise-' . bin2hex(random_bytes(8));
$catalog = new Catalogo([
    new DefinicaoEvento(
        'synthetic.connection_unavailable',
        'Synthetic dependency unavailable; retry scheduled.',
        Severidade::Alerta,
        Classificacao::Transitorio,
        ['attempt', 'retry_delay_ms'],
        resultado: Resultado::NovaTentativaAgendada,
        camposAgrupamento: [],
    ),
], []);
$registrar = new Registrador(
    new Configuracao('synthetic-project', 'worker', 'testing'),
    $catalog,
    new GravadorArquivoDiario($directory),
    new AgregarTransitorios(),
);
$firstId = $registrar->registrar(
    'synthetic.connection_unavailable',
    ['attempt' => 1, 'retry_delay_ms' => 100],
    correlacao: 'synthetic-operation-1',
);
$repetitionId = $registrar->registrar(
    'synthetic.connection_unavailable',
    ['attempt' => 2, 'retry_delay_ms' => 200],
    correlacao: 'synthetic-operation-1',
);
$registrar->descarregarRuido();
```

Expected result: `$firstId` is nonnull, `$repetitionId` is null, and explicit flush produces a second JSON Lines record with code `library.transient_summary`, `suppressed_count: 1`, `reason: explicit_flush` and last attempt/delay `2/200`. No recovery is asserted. The example uses the default 60-second window; executing calls across its expiry can instead create a fresh occurrence. Dispose only of this example's owned temporary output after inspection. Caller code must handle writer exceptions; see the partial-failure contract below.

<!-- reading-section: partial-failure -->
## Partial failure and safe diagnosis

Pending summaries are written before the current event. If a summary fails, the registrar attempts to write the current event anyway and then rethrows the summary error. Thus an exception does not prove the current event was absent. If that current write also fails, its error propagates instead. There is no rollback of previously written records. Blindly retrying the registration can create another occurrence UUID; there is no caller-supplied idempotency key or exactly-once guarantee. Explicit flush retry and repeating a business operation are different actions.

| Symptom | Safe diagnosis / recovery boundary |
| --- | --- |
| Legacy/incompatible directory | Preserve existing logs; choose an approved empty exclusive destination; no automatic conversion |
| Missing/replaced directory or unsafe link | Inspect ownership, mounts and inode changes; preserve targets; do not bypass identity checks |
| Oversized event | Review approved fields and byte limit; never dump rejected sensitive payloads into diagnostics |
| Incomplete/invalid edge record | Stop treating append as healthy; preserve file for authorized inspection; do not truncate it as routine validation |
| Write/sync/restoration failure | Check capacity, permissions and filesystem health; failed restoration needs file-integrity investigation |
| Delayed call | Check blocking file lock and synchronous I/O; no configured timeout exists |
| Missing final summary | Check process lifecycle, explicit flush and abrupt termination; absence is not proof of zero repetitions |
| Error after current event persisted | Inspect synthetic/authorized event evidence and adapter outcome before retry; delivery may be partial |

Do not recursively report a writer failure through the same writer. Host applications need a separately approved failure boundary that preserves their business semantics and privacy. This task adds no fallback channel or recovery implementation. Operators must arrange private backup/retention according to installation policy; no backup/restore procedure was executed and restoring files while writers are active is not validated.

<!-- reading-section: evidence -->
## Evidence and maintenance

Sources: `src/Infraestrutura/{GravadorArquivoDiario,SerializadorJson,GravadorPsr}.php`, `src/Registrador.php::{registrarDefinicao,gravarResumos,descarregarRuido}`, `src/Aplicacao/{AgregadorTransitorios,AgregarTransitorios,PreservarEventos}.php`. Assertions: `tests/Aplicacao/RuidoTest.php`, `tests/Infraestrutura/ArquivoDiarioTest.php`, `tests/Integracao/{ContratoRegistroTest,ProcessosTest}.php`. Reinspect both languages whenever grouping, writer identity/locking, flush, file acceptance or application lifecycle changes. Local process tests do not certify network filesystems, power-loss recovery, production storage, Datadog shipping or throughput.

## Storage identity migration

New files use UTC `tracepaw-YYYY-MM-DD.log` and the standalone writer uses `.tracepaw-lib-jsonl-v1`. Historical `datadog-YYYY-MM-DD.log` files remain untouched: do not rename, rewrite, convert markers or introduce compatibility readers. Consumer Monolog retention does not automatically remove files under the old prefix. Operators own retention and archival of those files.
