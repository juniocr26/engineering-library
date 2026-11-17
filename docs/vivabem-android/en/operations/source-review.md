> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — VivaBem Android

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `vivabem-android/app/build.gradle`
- `vivabem-android/app/src/main/java/br/com/vivabem/app/LauncherActivity.java`
- `vivabem-android/app/src/main/java/br/com/vivabem/app/VivaBemFirebaseMessagingService.java`
- `vivabem-android/tools/tests/test_verify_twa.py`

<!-- reading-section: history -->

## Historical reuse and corrections

The old map/interview supply TWA/browser ownership, DAL and notification-delivery boundaries. Earlier patient-versus-psychologist lifetime differences are superseded by the Portal rolling-inactivity implementation for current policy records. Existing store declarations are drafts, not proof of publication. Historical Android fingerprint variables belong to Portal configuration when consumed there, not automatically to the Android environment.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/vivabem-android.md`
- `engineering-library_old/docs/en/interviews/vivabem-android-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Installed-certificate verification, live DAL response, device/browser lifecycle, denied/stale push behavior, signed release and Play publication remain unverified. Token-to-authorization association and full session-specific delivery filtering require further investigation.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)
