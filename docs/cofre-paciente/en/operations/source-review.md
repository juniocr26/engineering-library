> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — Cofre Paciente

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `cofre-paciente/composer.json`
- `cofre-paciente/routes/api.php`
- `cofre-paciente/app/Http/Middleware/JwtMiddleware.php`
- `cofre-paciente/app/Services/CofreRequestPolicy.php`
- `cofre-paciente/app/Repository/CartoesRepository.php`
- `cofre-paciente/app/Services/StoredFinancialReader.php`
- `cofre-paciente/app/UseCases/CartoesUseCase.php`
- `cofre-paciente/app/UseCases/LinksUseCase.php`
- `cofre-paciente/config/crypto.php`
- `cofre-paciente/config/services.php`
- `cofre-paciente/tests/Feature/F06AuthorizationTest.php`

<!-- reading-section: history -->

## Historical reuse and corrections

The historical map supplies selective-encryption, local/remote cleanup and Mongo-boundary explanations. Its conta_bancarias API and earlier bank-map CAS exercise are retired, not active interfaces. A generic service-JWT explanation is incomplete for the current nine-route request policy. Historical whole-list failure descriptions are superseded by explicit partial-read completeness.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/cofre-paciente.md`
- `engineering-library_old/docs/en/interviews/cofre-paciente-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Real Mongo concurrency, full ratings lifecycle/index audit, confirmed queue handoff/recovery, remote conference acceptance, backup restoration and end-to-end actor ownership remain outside this selective review. No Mongo, broker or external API was contacted.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)

Additional focused source reading: `app/Services/GoogleMeetRemovalMessageProcessor.php`, `app/Services/ConfirmedRabbitMqPublisher.php`, `app/Console/Commands/ConsumirRemocaoGoogleMeetCommand.php`.

Additional focused source reading: `app/Services/Avaliacoes/RatingLifecycleService.php`, `app/Services/Avaliacoes/EvaluationIndexMaintenance.php`.
