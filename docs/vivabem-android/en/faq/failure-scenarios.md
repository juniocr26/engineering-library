# Failure reasoning — VivaBem Android

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

Native preferences contain local notification/token state; Portal databases remain authoritative for appointments and identity. Gradle validates the existing fixed debug keystore only during debug signing, with no generated fallback. Release signing requires the existing upload keystore and environment passwords. Upload, debug and Play-distributed certificates are distinct identities; a successful local build does not establish the installed Play signing certificate.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Review LauncherActivity, messaging service and app/build.gradle before considering build changes. For a future authorized device check, test a hostile deep link, missing notification permission, logout/current-context revocation, delayed push and a certificate mismatch. Preserve fixed signing identity; do not regenerate keys to make a build pass. Build, signing, Play upload and release are separate procedures and were not executed here.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
