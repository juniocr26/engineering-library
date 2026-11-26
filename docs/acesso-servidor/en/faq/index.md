# Technical FAQ — acesso-servidor

[English](index.md) | [Português brasileiro](../../pt-br/faq/index.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: q001 -->

## Q001 — Is --dry-run a safe read-only documentation check?

No. It selects validation mode but cleanup_dependencies still removes dependency directories and exact audit proposals before preflight. A later failure does not restore them. Inspect source without invoking the updater.

<!-- reading-section: q002 -->

## Q002 — Does failure restore all four applications?

No. The workflow is sequential and has no automatic global rollback. Record completed branch/build/startup phases, preserve data and original identities, then plan compatible recovery. A successful readiness probe is not a tested restore procedure.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Authorized-server deployment, full startup order, original-data restoration, cross-version compatibility and recovery from interrupted cleanup were not executed. No updater mode, Git update, SSH, reset or migration ran.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
