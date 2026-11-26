# Testing and acceptance — acesso-servidor

[English](strategy.md) | [Português brasileiro](../../pt-br/testing/strategy.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: assertions -->

## Inspected assertions

`tests/test_operator_workflow.py`: Creates disposable Git/secret fixtures and mocks selected updater functions; asserts original-byte preservation and operator workflow. Fixture success would not establish deployment acceptance. This suite was not executed.

<!-- reading-section: proposed -->

## Proposed verification

For investigation, read main, compose, cleanup_dependencies and deployment_guard.git_state before using any CLI flag. Review exact branches, initial tree state, existing configuration and backup/restore evidence in a separately authorized maintenance window. If a phase fails, identify completed phases and preserve logs/original keys; do not assume an automatic rollback or retry the entire updater blindly. This collection deliberately gives no runnable production deployment command.

<!-- reading-section: not-run -->

## Execution boundary

Application tests were not run. No historical count is claimed as current. Documentation checks are recorded separately in the library review.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
