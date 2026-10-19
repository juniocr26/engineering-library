# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

Literal parse/plan/write flow, preview-to-write race, per-file recovery, plaintext backup boundaries and absence of application ENV configuration.

Inspected Git HEAD (not a guarantee of a clean tree): `3bfe68e30a4169219f69b65ccc6188d5c5f5263f`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `scripts/audit-envs.py`
- `tests/test_audit_envs.py`

## Category review in this pass

- [architecture/overview.md](../architecture/overview.md)
- [architecture/implementation-review.md](../architecture/implementation-review.md)
- [guides/implementation-study.md](../guides/implementation-study.md)
- [security/filesystem-boundaries.md](../security/filesystem-boundaries.md)
- [operations/recovery-and-evidence.md](../operations/recovery-and-evidence.md)
- [operations/source-review.md](../operations/source-review.md)
- [testing/verification.md](../testing/verification.md)
- [env/index.md](../env/index.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Complete line-by-line review of every retained legacy answer, both READMEs, remaining terminal/guide pages and all test bodies; reconcile historical test counts without turning them into current runs.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
