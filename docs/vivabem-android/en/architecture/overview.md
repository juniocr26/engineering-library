# Architecture and integration boundaries

[Contents](../index.md)

## Verified state and public boundaries — 2026-11-11

Android TWA using Android Browser Helper and a native Firebase notification bridge. Web authentication belongs to the Portal/browser; signing and origin verification belong to Android distribution. It does not share PHP Composer dependencies and no direct TracePaw integration was established. Build, publication and actual push delivery were not executed in this review.

Source inspection and local metadata do not confirm Docker image contents, deployment, mounts or external acceptance. This public summary omits internal endpoints, topology, identifiers and private rules; full operational contracts remain in source repositories. No database catalog synchronization was performed.
