# Technical FAQ — script-auditoria-envs

[English](index.md) | [Português brasileiro](../../pt-br/faq/index.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: q001 -->

## Q001 — Is the default invocation read-only?

No. It synchronizes targets, including removals after backups. Preview requires --dry-run or --audit-only; always provide a disposable explicit root when studying behavior.

<!-- reading-section: q002 -->

## Q002 — Can a successful proposal be considered activated?

No. It proves file-level work only. Cached configuration and long-lived processes may retain old state. Check the relevant consumer activation procedure rather than retrying the proposal blindly after partial progress.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Crash recovery, uncooperative-editor races, named ACL behavior on every filesystem and complete activation across consumers remain unverified. No CLI was run against real configuration.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
