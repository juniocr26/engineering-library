# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

The original audit covered catalog metadata synchronization, PostgreSQL persistence, filesystem readers and current-vs-future architecture. The later shared-annotation transition is documented in [current architecture](../architecture/current-state.md); it supersedes the persistence access model from this historical audit.

Inspected Git HEAD (not a guarantee of a clean tree): `7b96b3545d5f257611257d23846606cbdefc0442`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `compose.yaml`
- `backend/config/routes.rb`
- `backend/config/database.yml`
- `backend/config/initializers/cors.rb`
- `backend/db/schema.rb`
- `backend/app/services/catalog/files.rb`
- `backend/app/services/catalog/sync.rb`
- `backend/app/services/catalog/page.rb`
- `backend/app/services/catalog/presenter.rb`
- `backend/app/controllers/api/projects_controller.rb`
- `backend/app/controllers/api/bookmarks_controller.rb`
- `backend/app/models/catalog_project.rb`
- `backend/app/models/bookmark.rb`
- `backend/test/models/catalog_test.rb`
- `backend/test/integration/catalog_api_test.rb`
- `backend/test/integration/bookmarks_api_test.rb`
- `frontend/lib/catalog.ts`
- `frontend/lib/documentation.ts`
- `frontend/lib/document-links.ts`
- `frontend/lib/reading-order.ts`
- `frontend/lib/source-links.ts`
- `frontend/lib/source-snapshot.ts`
- `frontend/lib/source-search.ts`
- `frontend/tests/reading-order.test.ts`
- `frontend/package.json`
- `docs/validation/check_catalog.py`
- `tools/check_docs.py`
- `tools/test_catalog.py`

## Category review in this pass

- [architecture/current-state.md](../architecture/current-state.md)
- [architecture/future-direction.md](../architecture/future-direction.md)
- [architecture/source-references.md](../architecture/source-references.md)
- [guides/book-frontend.md](../guides/book-frontend.md)
- [guides/documentation-validator.md](../guides/documentation-validator.md)
- [guides/application-development.md](../guides/application-development.md)
- [env/index.md](../env/index.md)
- [testing/documentation.md](../testing/documentation.md)
- [operations/source-review.md](../operations/source-review.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Review the complete reader components, pagination/media/Mermaid rendering, source-catalog generator/runtime loader, remaining setup/operations guides and migrations/tasks. Reconcile old verification narratives against their dates; execute browser checks only in a suitable existing runtime.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
