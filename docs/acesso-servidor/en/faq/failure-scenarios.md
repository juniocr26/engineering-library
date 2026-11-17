# Failure reasoning — acesso-servidor

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

Original encryption identity, publisher identity, build SSH material, dependencies, application storage and private logs have different lifetimes. Guard functions reject unsafe roots/symlink ancestors and branch collisions before mutations. Application startup may run migrations without the optional --migrate flag: preserving data is not a promise of no writes. Explicit Mongo removal has a separate guarded target/terminal decision; it is not a generic SQL reset.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

For investigation, read main, compose, cleanup_dependencies and deployment_guard.git_state before using any CLI flag. Review exact branches, initial tree state, existing configuration and backup/restore evidence in a separately authorized maintenance window. If a phase fails, identify completed phases and preserve logs/original keys; do not assume an automatic rollback or retry the entire updater blindly. This collection deliberately gives no runnable production deployment command.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
