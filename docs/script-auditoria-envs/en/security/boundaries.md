# Trust boundaries — script-auditoria-envs

[English](boundaries.md) | [Português brasileiro](../../pt-br/security/boundaries.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: mechanisms -->

## Mechanisms and limits

Discovery skips symbolic directories/files and exact excluded dependency/build paths; it is not a universal secret-directory sandbox. Proposal mode uses no-follow descriptors and cooperative locking. Noncooperating editors and platform/filesystem semantics remain limits. Backups are plaintext sensitive material; restrictive permissions are not encryption. Default scanning can include unrelated siblings and must never be used as a documentation check.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
