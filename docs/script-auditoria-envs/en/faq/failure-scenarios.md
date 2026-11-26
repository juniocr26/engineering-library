# Failure reasoning — script-auditoria-envs

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

The data model is ordered blocks, name sets and file snapshots, not a database. `atomic_write` fsyncs a temporary file then replaces one path. `env_apply.apply_directory` locks the directory, checks input snapshots and ownership/ACL preservation, writes `.env` then `.env.example`, verifies, then cleans proposals. A failure between replacements leaves partial progress; the pair and workspace are not one transaction.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

For a future isolated exercise, create a disposable directory containing synthetic `.env` and `.env.example` with SHARED, ONLY_TARGET and ONLY_EXAMPLE names. Invoke `python3 audit-envs.py /absolute/synthetic-root --dry-run` from this source repository to inspect name actions. Only separately authorize a write mode after reviewing its exact scope. A successful write does not refresh Laravel caches, rebuild containers or restart workers; activation is a separate application procedure.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
