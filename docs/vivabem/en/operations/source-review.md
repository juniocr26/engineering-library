> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — VivaBem

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `f0b884ca536a26996d40bf4187981d8c7506d0d7`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `vivabem/composer.json`
- `vivabem/app/Services/DashboardReadService.php`
- `vivabem/app/Services/BalanceReader.php`
- `vivabem/app/Services/ExternalPosterCofrePaciente.php`
- `vivabem/app/Services/ExternalPosterDigitalWallet.php`
- `vivabem/app/Services/CofreRequestPolicy.php`
- `vivabem/app/Services/RedisAuthenticationSession.php`
- `vivabem/app/Services/OfficialAppRequestDetector.php`
- `vivabem/app/Services/HubEventSigner.php`
- `vivabem/app/Services/AuditExecutor.php`
- `vivabem/config/cofre-paciente.php`
- `vivabem/config/carteira-digital.php`
- `vivabem/config/android.php`
- `vivabem/config/crypto.php`
- `vivabem/config/services.php`
- `vivabem/tests/Feature/BalanceReaderTest.php`

<!-- reading-section: history -->

## Historical reuse and corrections

The old architecture/interview supply state ownership, missed-notice recovery, local transaction limits and dashboard reasoning. Stripe-funded appointment/payout/outbox descriptions are historical after financial retirement. The current dedicated balance client must not be conflated with the unavailable generic wallet adapter. Legacy policy records retain their own bounded semantics; current 60-day policy and nonqualifying passive activity supersede blanket TTL claims. Audit selected-directory CLI support does not prove the Portal uses it.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/vivabem.md`
- `engineering-library_old/docs/en/interviews/vivabem-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

This review samples dashboard, peer transport, balance/authentication and audit boundaries. Complete appointment state-machine/recovery, conference lifecycle, mail/FCM delivery, queue recovery, UI accessibility, database concurrency and production startup/restore acceptance remain unverified here. Existing detailed source documentation must be rechecked against those implementations before expanding claims.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)

Additional focused source reading: `routes/web.php`, `app/UseCases/AtendimentoUseCase.php`, `app/UseCases/AtendimentoEmergencialUseCase.php`, `app/Http/Controllers/TransacaoController.php`, `app/Jobs/ProcessarBuscaAtendimentoEmergencial.php`, `app/Services/AtendimentoGoogleMeetLinkService.php`, `app/Services/AtendimentoMensalGoogleMeetCleanupService.php`.
