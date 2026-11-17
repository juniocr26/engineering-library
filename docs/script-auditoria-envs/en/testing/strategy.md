# Testing and acceptance — script-auditoria-envs

[English](strategy.md) | [Português brasileiro](../../pt-br/testing/strategy.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: assertions -->

## Inspected assertions

`tests/test_selected_directory.py`: Synthetic fixtures assert mode/owner preservation, unrelated-file preservation, probe failure and existing-target requirement.

<!-- reading-section: proposed -->

## Proposed verification

For a future isolated exercise, create a disposable directory containing synthetic `.env` and `.env.example` with SHARED, ONLY_TARGET and ONLY_EXAMPLE names. Invoke `python3 audit-envs.py /absolute/synthetic-root --dry-run` from this source repository to inspect name actions. Only separately authorize a write mode after reviewing its exact scope. A successful write does not refresh Laravel caches, rebuild containers or restart workers; activation is a separate application procedure.

<!-- reading-section: not-run -->

## Execution boundary

Application tests were not run. No historical count is claimed as current. Documentation checks are recorded separately in the library review.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
