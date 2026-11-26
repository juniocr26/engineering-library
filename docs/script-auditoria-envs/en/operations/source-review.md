> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — script-auditoria-envs

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `script-auditoria-envs/audit-envs.py`
- `script-auditoria-envs/env_sync.py`
- `script-auditoria-envs/env_apply.py`
- `script-auditoria-envs/tests/test_selected_directory.py`

<!-- reading-section: history -->

## Historical reuse and corrections

The old implementation map and interview supply literal-preservation, backup and partial-write explanations. Earlier claims that an audit analyzes source usage or that the portal audit was only future are not adopted. The current CLI includes selected-directory proposal application; Portal integration requires inspection of its executor as a separate authority.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/script-auditoria-envs.md`
- `engineering-library_old/docs/en/interviews/script-auditoria-envs-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Crash recovery, uncooperative-editor races, named ACL behavior on every filesystem and complete activation across consumers remain unverified. No CLI was run against real configuration.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)
