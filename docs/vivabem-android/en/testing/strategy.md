# Android verification: DAL checks and untested native boundaries

[Contents](../index.md) | [Português brasileiro](../../pt-br/testing/strategy.md)

Reviewed/executed 2026-11-10 at b2287cf. Audience: Android maintainers and release reviewers. This is a Java TWA client; tests here do not exercise a separate application backend.

<!-- reading-section: suite -->
## Existing offline suite

`tools/tests/test_verify_twa.py` uses Python unittest and imports tools/verify-twa.py. Seven tests cover matching/mismatched certificates, package/namespace/relation constraints, malformed and multiple statements, lowercase fingerprints, redirect rejection, invalid payload and refusal to overwrite the Portal's canonical association file. The last case reads that public JSON and asserts it remains unchanged; no signing key or real credential is read. This suite does not request live HTTPS or start Gradle.

<!-- reading-section: execution -->
## Actual result

From repository root:

```sh
python3 -B -m unittest discover -s tools/tests -v
```

Exit 0: **7 tests passed**, 2026-11-10. No APK/AAB, emulator, device, Firebase delivery or store publication was executed. Historical 2026-10-04 unsigned debug/release build and six-test statements remain historical; the 2026-11-04 seven-test report was not substituted for this new execution.

<!-- reading-section: native -->
## Native behavior inspected, not device-tested

LauncherActivity accepts only the configured HTTPS host without userinfo/explicit port, falls back to safe app-entry, appends source=android, requests Android 13+ notification permission and closes PonteRegistroPush on destruction. The marker is not backend authentication.

PonteRegistroPush validates Custom Tabs origin relationship, waits for navigation/channel readiness, accepts bounded request IDs, sends the stored FCM token only for an active request and clears channel/request/listeners on close. It exchanges no account password. ServicoMensagensFirebaseVivaBem stores refreshed token, supports cancel/display, checks permission and sanitizes navigation origin; critical notifications have a 120-second timeout. None of these native lifecycle/security decisions is covered by the Python DAL suite.

<!-- reading-section: build -->
## Build, security and acceptance limits

app/build.gradle declares Firebase Messaging and Android Browser Helper, fixed debug signing validation, conditional release signing, source MP4 packaging and generated launcher/store resources. A successful DAL parser test does not establish deployed certificate association, browser postMessage support, release signing, permission behavior or background delivery. No signing material was regenerated and no google-services credential content was inspected.

Before release acceptance, separately verify approved signing identity, deployed DAL without redirects, hostile deep links, denied notification permission, bridge navigation/reset, token rotation, current-session revocation and delayed/cancelled push on devices. These are missing validation boundaries, not newly implemented tests or an approved release. Portal owns accounts, appointments/payments and session authorization; native token storage is not an offline financial or patient database.

Sources: app/build.gradle; app/src/main/java/br/com/vivabem/app/LauncherActivity.java, PonteRegistroPush.java, ServicoMensagensFirebaseVivaBem.java; tools/tests/test_verify_twa.py. Recheck both languages and collection after origin, bridge protocol, signing, SDK or suite changes.
