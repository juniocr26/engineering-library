# Public PHP API and structured event contract

[Contents](../index.md) | [Português brasileiro](../../pt-br/api/contracts.md)

Reviewed 2026-11-10; A: inspected API. Audience: PHP callers and event consumers. This is an in-process API, with no HTTP authentication, endpoints or response status codes. Caller authorization belongs to the host application. See [installation](../guides/installation.md), [privacy](../security/context-and-diagnostics.md) and [reliability](../operations/reliability.md).

<!-- reading-section: registrar -->
## Registrar methods and error semantics

`TracePaw\Registrador` takes `Configuracao`, `Catalogo`, `Gravador`, optional `PoliticaRuido` (default `PreservarEventos`), optional `SanitizadorContexto` and optional `AgregadorTransitorios`. Named arguments must retain their Portuguese spelling.

```php
public function registrar(
    string $codigo,
    array $contexto = [],
    array $tags = [],
    ?string $correlacao = null,
    ?string $requisicao = null,
    ?Resultado $resultado = null,
    ?\Throwable $excecao = null,
): ?string;

public function registrarFalhaInesperada(
    \Throwable $excecao,
    ?string $correlacao = null,
    ?string $requisicao = null,
): string;

public function descarregarRuido(): void;
```

`registrar` returns an occurrence UUID after writer success, or `null` for an aggregated repetition. It does not return a boolean business outcome. Identifiers, when supplied, match `[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}`; empty strings/newlines are invalid. Unknown codes, conflicting default tags, contradictory fixed outcomes and invalid approved context throw `InvalidArgumentException`. PHP type errors remain type errors. Writer failures propagate; there is no success envelope or automatic retry.

`registrarFalhaInesperada` bypasses catalog lookup with `library.unexpected_failure`, static Portuguese message, `error`, `unexpected_defect`, empty context/tags and outcome `unknown`, using sanitized exception diagnostics. It still validates correlation/request IDs and can fail when writing. It is not an automatic fallback for misspelled event codes.

<!-- reading-section: definitions -->
## Definitions and controlled taxonomy

`Dominio\DefinicaoEvento` constructor fields, in order: `codigo`, `mensagem`, `severidade`, `classificacao`, `camposPermitidos=[]`, `tags=[]`, `impacto=null`, `resultado=Resultado::Desconhecido`, `acaoNecessaria=null`, `camposAgrupamento=null`. Code has at least two dot-separated lowercase segments, each beginning with a letter, using letters/digits/underscores; maximum 128 bytes. Message is nonempty UTF-8, at most 2048 bytes; optional impact is UTF-8, at most 256 bytes. Messages are fixed catalog content, not caller-interpolated payloads.

`Aplicacao\Catalogo(array $definicoes, array $taxonomia)` rejects non-definitions, duplicate codes, unapproved default tags and invalid taxonomies. Allowed tag dimensions are exactly `domain`, `component`, `dependency`, `operation`, `failure_category` (`Dominio\Tags::DIMENSOES`). A taxonomy dimension accepts up to 100 strings matching `[a-z][a-z0-9_]{0,63}`. `Tags` trims/lowercases incoming key/value pairs, rejects normalization collisions or unapproved values, and sorts keys. IDs and URLs belong outside this low-cardinality vocabulary; syntactic approval alone cannot guarantee a privacy-safe catalog.

| PHP severity | Serialized severity |
| --- | --- |
| `Depuracao` | `debug` |
| `Informacao` | `info` |
| `Aviso` | `notice` |
| `Alerta` | `warning` |
| `Erro` | `error` |
| `Critico` | `critical` |
| `AcaoImediata` | `alert` |
| `Emergencia` | `emergency` |

`Classificacao` values: `Esperado=expected`, `Transitorio=transient_failure`, `Recuperavel=recoverable_error`, `Recuperacao=confirmed_recovery`, `Defeito=unexpected_defect`, `Incidente=operational_incident`, `Seguranca=security_incident`. `Resultado` values: `Desconhecido=unknown`, `Sucesso=success`, `Falha=failure`, `NovaTentativaAgendada=retry_scheduled`, `Esgotado=retry_exhausted`, `PossivelPerda=potential_data_loss`. These are separate dimensions. A definition with outcome `unknown` permits caller selection; a fixed outcome cannot be contradicted. The library records what callers assert; it does not verify recovery or schedule retries.

<!-- reading-section: catalog -->
## Synthetic catalog and internally generated events

`Catalogo::exemplosSinteticos()` is an example vocabulary, not proof of producer deployment. Context columns below list approved optional fields; absent fields are omitted.

| Code | Severity / classification | Context | Fixed outcome |
| --- | --- | --- | --- |
| `consumer.processing_started` | info / expected | attempt | unknown |
| `dependency.retry_scheduled` | notice / expected | attempt, retry_delay_ms, retry_scheduled (only true) | retry_scheduled |
| `redis.connection_unavailable` | warning / transient_failure | attempt, duration_ms | unknown |
| `redis.connection_recovered` | info / confirmed_recovery | duration_ms | success |
| `rabbitmq.consumer_interrupted` | error / recoverable_error | attempt | unknown |
| `application.unexpected_failure` | error / unexpected_defect | duration_ms | unknown |
| `operation.retry_exhausted` | critical / operational_incident | attempt | retry_exhausted |

The example taxonomy defines domain `messaging/application`, component `connection/consumer/runtime`, dependency `redis/rabbitmq`, operation `connect/consume/execute/publish/process/schedule_retry` and failure category `connection_unavailable/connection_interrupted/unexpected_failure/retry_exhausted`. Default tags are declared per definition in `src/Aplicacao/Catalogo.php`; callers cannot replace them with conflicting values.

`library.unexpected_failure` is generated only by the explicit unexpected-failure method. `library.transient_summary` is generated by aggregation and is not resolved through this catalog. A summary retains original severity/tags/outcome/IDs of request and correlation, but receives its own event UUID and timestamp; `first_event_id` points to the original occurrence. Details and counts are in [reliability](../operations/reliability.md).

<!-- reading-section: schema -->
## Schema version 1.1 and JSON Lines

`Dominio\Evento::paraArray` emits the following contract. `Infraestrutura\SerializadorJson::serializar` encodes Unicode/slashes without escaping, preserves zero fractions, substitutes invalid UTF-8 and appends exactly one physical newline. Newlines inside text are JSON escapes. Empty `tags` and `context` are JSON objects, not arrays.

| Fields | Type and meaning |
| --- | --- |
| `schema_version` | string `1.1`; writer also accepts boundary records marked `1.0` |
| `event_id`, `timestamp` | UUID v4 from registrar; UTC `Y-m-dTH:i:s.uZ` |
| `project`, `service`, `environment` | configured producer strings |
| `severity`, `event_code`, `message`, `classification` | catalog semantics |
| `tags`, `context` | controlled object, sanitized scalar object |
| `impact`, `action_required` | nullable string, nullable boolean from definition |
| `outcome` | enum string, never inferred from severity |
| `request_id`, `correlation_id` | nullable caller-supplied identifiers |
| `exception` | optional diagnostic object; omitted without Throwable |
| `aggregation` | optional summary object; omitted on ordinary events |

`SerializadorJson($limiteBytes=65536)` accepts limits 4096–1048576 inclusive; the newline counts toward the byte limit. Oversized or unserializable events throw `Dominio\FalhaGravacao`; JSON errors retain their cause. Current emission version and writer acceptance are different contracts: accepting `1.0` at file boundaries neither converts old records nor guarantees every consumer supports `1.1`.

Constructing `Evento` directly bypasses registrar validation/sanitization. Writers serialize the object they receive; they are not a second privacy validator. Normal integrations should use `Registrador` and reviewed definitions.

<!-- reading-section: evidence -->
## Evidence and maintenance

Sources: `src/Registrador.php`; `src/Dominio/{DefinicaoEvento,Tags,Severidade,Classificacao,Resultado,Evento}.php`; `src/Aplicacao/Catalogo.php`; `src/Infraestrutura/SerializadorJson.php`. Existing assertions: `tests/Aplicacao/{CatalogoTest,RegistradorTest}.php`, `tests/Dominio/{EventoTest,TagsTest}.php`, `tests/Infraestrutura/SerializadorTest.php`. Executed results are separate in verification. Recheck both languages and downstream readers whenever constructor parameters, enums, synthetic catalog, schema or writer version acceptance changes. No live collector compatibility or released-package matrix was executed.
