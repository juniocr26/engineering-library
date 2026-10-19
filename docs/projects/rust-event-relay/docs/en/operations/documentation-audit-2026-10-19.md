# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

Dedicated demo intent/actions, identity reconciliation, HTTP admission/timeout, new multiple-action migration and selected test definitions.

Inspected Git HEAD (not a guarantee of a clean tree): `a1e0fa1513a8cbdf362f06f5cf1bdd906eb2430c`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `backend/src/application/demo.rs`
- `backend/src/infrastructure/demo_http.rs`
- `backend/src/bin/demo.rs`
- `backend/src/infrastructure/postgres/demo.rs`
- `backend/migrations/20261019000000_multiple_duplicate_actions.up.sql`
- `backend/migrations/20261019000000_multiple_duplicate_actions.down.sql`
- `backend/tests/demo_runs.rs`

## Category review in this pass

- [architecture/overview.md](../architecture/overview.md)
- [database/migrations.md](../database/migrations.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Audit the full producer/relay/consumer/replay/retry/ownership paths, broker and SQL adapters, frontend/proxy, supervisor/start scripts, topology/ENV, all ADRs/migrations and remaining milestone evidence. Current demo inspection is not a full delivery-guarantee audit.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
