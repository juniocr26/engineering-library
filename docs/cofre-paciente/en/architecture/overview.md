# Architecture and integration boundaries

## Server architecture — 2026-11-16

Server deployment combines the base Compose configuration with its server overlay and uses externally managed MongoDB. The overlay removes the local `mongo` service and its database-only mount; application dependencies and manager endpoints are adjusted. The application builds from `docker/Dockerfile.server`, reusing existing runtime clients and entrypoints. Development retains its original local database service and persistence. Removing a mount from configuration is not migration or physical deletion of existing data.

[Operational status and limits](../operations/index.md) · [Connection interface](../env/index.md)

[Contents](../index.md)

## Verified state and public boundaries — 2026-11-11

Laravel service with MongoDB and cryptographic integration. The verified scope stores encrypted references and specific collections, not a general clinical record. Authentication, authorization and data protection are distinct responsibilities. Decryption failure, incomplete reads, confirmed deletion and uncertain outcomes must remain distinguishable. TracePaw receives minimized events; clinical data and payment references must not become log context.

All three consumers declare and lock `parceiro-vivabem/tracepaw-lib 0.2.0`; local installed metadata records the same version. Channel `tracepaw`, namespace `TracePaw` and `tracepaw-YYYY-MM-DD.log` are current contracts. Monolog owns formatting/rotation/retention; the internal JSONL writer is a different adapter. Historical logs remain untouched.

Source inspection and local metadata do not confirm Docker image contents, deployment, mounts or external acceptance. This public summary omits internal endpoints, topology, identifiers and private rules; full operational contracts remain in source repositories. No database catalog synchronization was performed.
