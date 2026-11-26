# Trust boundaries — acesso-servidor

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

Deployment requires an authorized target and original identities. Guard root/path checks constrain operations but cannot make a partially completed multi-project rollout atomic. A crypto roundtrip validates that consumer/configuration path, not every stored record or record ownership. Private logs can retain sensitive operational context and must not be published. No secret directory, SSH key, PEM, server credential or database was opened in this task.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
