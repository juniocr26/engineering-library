# Installation, configuration and first event

[Contents](../index.md) | [Português brasileiro](../../pt-br/guides/installation.md)

Reviewed 2026-11-10. Audience: PHP integrators. Objective: instantiate the actual public API and produce a synthetic JSON Lines event in a disposable location. A: inspected API; the example is illustrative unless separately recorded as executed. This guide does not install the package into any ecosystem application.

<!-- reading-section: prerequisites -->
## Requirements and Composer identity

`composer.json` requires PHP `^8.2`, JSON and `psr/log ^3.0`; package name is `parceiro-vivabem/tracepaw-lib`, namespace `TracePaw\`. Consumers need an owner-approved private Composer source exposing that identity. The repository does not establish a public registry URL or a release/version constraint suitable for every application. Do not invent one or embed credentials in project configuration.

From an authorized consumer, after its approved private repository and version policy are configured, the package-name command is:

```sh
composer require parceiro-vivabem/tracepaw-lib:0.2.0
```

This modifies the consumer's manifest/lockfile/vendor and can access the configured package source; it was not executed during documentation work. A maintainer checking out the library uses its existing lockfile and `composer install` when dependencies are missing. Installation is distinct from verification and is not needed when `vendor/` already exists. Inspect the resolved version before claiming that these checkout contracts apply to a deployed application.

<!-- reading-section: configuration -->
## Configuration contract

The inspected `src/` reads no dotenv/environment variable directly. Callers supply constructor arguments; application-specific environment names are not prescribed. Empty and absent values must not be guessed from a Laravel convention.

| Input / declaring constructor | Default and validation | Operational meaning |
| --- | --- | --- |
| `Configuracao($projeto,$servico,$ambiente)` | All required; `[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}` | Static nonsecret producer identity; empty strings rejected |
| `Catalogo($definicoes,$taxonomia)` | Both arrays required; see API reference | Reviewed vocabulary, not arbitrary runtime payload |
| `GravadorArquivoDiario($diretorio,$serializador)` | Directory required; serializer defaults to `new SerializadorJson()` | Constructor creates/initializes storage; use dedicated path |
| `SerializadorJson($limiteBytes)` | 65536; inclusive range 4096–1048576 | Counts bytes including newline; error on overflow |
| Registrar `politica` | `new PreservarEventos()` | Aggregation is opt-in |
| Registrar `sanitizador` | `new SanitizadorContexto()` | Default exception diagnostics omit source paths |
| `AgregadorTransitorios($intervaloMs,$limiteRepeticoes,$limiteGrupos,$relogio)` | 60000 / 100 / 256 / `hrtime(true)` | Ranges 1–3600000 ms, 1–10000 repetitions, 1–1024 groups |
| `DiagnosticoExcecao($raizAplicacao,$mensagensAprovadas,$limiteQuadros,$limiteCausas)` | null / [] / 12 / 3 | Existing non-root directory if supplied; frames 0–16; causes 1–4 |

`InvalidArgumentException` reports invalid identities, limits or diagnostic configuration. Storage initialization can throw `FalhaGravacao` before any event is registered. Paths and identity labels must be approved nonsecret values. Directory canonicalization and identity checks do not replace host-level access control; existing directory permissions are not automatically tightened by the constructor.

<!-- reading-section: first-event -->
## Synthetic PHP example

Run from the library checkout with installed dependencies. The example creates a unique temporary directory and writes one synthetic record; it never targets application logs. It requires filesystem write permissions. Do not paste it into a production request handler as a directory-allocation strategy.

```php
<?php

declare(strict_types=1);
require getcwd() . '/vendor/autoload.php';

use TracePaw\Aplicacao\{Catalogo, Configuracao};
use TracePaw\Infraestrutura\GravadorArquivoDiario;
use TracePaw\Registrador;

$directory = sys_get_temp_dir() . '/synthetic-events-' . bin2hex(random_bytes(8));
$registrar = new Registrador(
    new Configuracao('synthetic-project', 'worker', 'testing'),
    Catalogo::exemplosSinteticos(),
    new GravadorArquivoDiario($directory),
);
$eventId = $registrar->registrar(
    'consumer.processing_started',
    ['attempt' => 0],
    correlacao: 'synthetic-operation-1',
    requisicao: 'synthetic-request-1',
);
```

Expected observation: a nonnull UUID, `.tracepaw-lib-jsonl-v1` marker and `tracepaw-<UTC-date>.log` containing one newline-terminated JSON object with `schema_version: "1.1"`, code `consumer.processing_started` and `context.attempt: 0`. The file prefix is a storage convention, not proof of Laravel integration. Verify with a JSON parser against the disposable file; do not print real operational logs. Temporary example output needs an explicit local cleanup policy; this guide contains no production deletion command.

<!-- reading-section: adapter -->
## PSR-3 wiring and Laravel adoption

For an already-approved `Psr\Log\LoggerInterface` instance, inject `new TracePaw\Infraestrutura\GravadorPsr($logger)` as the writer. `GravadorPsr::gravar` serializes then decodes the event and calls `log($severity, $staticMessage, $structuredData)`. Nested object shape is retained. Logger exceptions are wrapped in `FalhaGravacao` with their cause; serializer failures occur before dispatch. The adapter implements the library's `Gravador`, not `LoggerInterface` itself.

The external logger controls formatting, storage, delivery and retention. A PSR-3 call does not guarantee JSON Lines, daily rotation, flush, remote acknowledgement or equivalent privacy for extra metadata appended by the logger. Review its configuration separately. No Datadog credentials or endpoint are required by this library's constructors.

Laravel adoption is present in the three consumers through PSR/Monolog adapters. Dedicated catalogs, lifecycle, failure handling and retention belong to each application. Deployment remains unverified; do not reuse a mixed-format log directory with the standalone exclusive writer.

<!-- reading-section: troubleshooting -->
## Verification, troubleshooting and maintenance

Unknown code: inspect `Catalogo::resolver` and the chosen definition set. Invalid context: inspect approved field type, bounds and lists rather than coercing business data to strings. Invalid tags: check approved taxonomy and contradictory defaults. Storage failure: follow [reliability](../operations/reliability.md), preserving existing evidence. Avoid recursive logging of writer errors through the same broken writer.

Sources: `composer.json`, `src/Aplicacao/{Configuracao,Catalogo,AgregadorTransitorios,DiagnosticoExcecao}.php`, `src/Registrador.php`, `src/Infraestrutura/{GravadorArquivoDiario,GravadorPsr,SerializadorJson}.php`. Executed suite and example validation are recorded in [verification](../testing/verification.md). Maintainers must review this guide with both languages after constructor, package requirement, deployment or adapter changes. Private registry access and production wiring remain unverified.

## Current adoption — 2026-11-11

All three Laravel consumers use dependency `0.2.0` in manifests, lockfiles and local installed metadata, with channel `tracepaw` and the PSR/Monolog adapter. Node.js Hub does not install this PHP library. The internal writer requires empty/exclusive storage and marker `.tracepaw-lib-jsonl-v1`; Monolog does not use that marker. Deployment and remote publication remain unverified; earlier future-adoption references describe the historical scope of the isolated library review.
