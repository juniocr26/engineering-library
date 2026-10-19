# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

Multipart contracts, defaults, proxy buffering, encoded/pixel resource boundaries and selected HTTP test definitions.

Inspected Git HEAD (not a guarantee of a clean tree): `cdb188c6a08f08482060a43d3d505fd494a1189e`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `backend/internal/infrastructure/http/handler/compress_image/handler.go`
- `backend/internal/infrastructure/http/handler/resize_image/handler.go`
- `backend/internal/infrastructure/http/handler/convert_image/handler.go`
- `backend/internal/infrastructure/http/router.go`
- `backend/internal/infrastructure/http/server.go`
- `backend/internal/infrastructure/imaging/limits.go`
- `backend/internal/infrastructure/http/resize_test.go`
- `frontend/app/api/images/forward-image-request.ts`
- `frontend/app/api/images/compress/route.ts`

## Category review in this pass

- [api/contracts.md](../api/contracts.md)
- [security/resource-boundaries.md](../security/resource-boundaries.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Inspect all use cases and codec implementations/fixtures, frontend controls/download lifecycle, Docker/CGO configuration, ENV consumers, ADR and remaining tests; revalidate every retained legacy answer.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
