# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

Read-only catalog DTOs, query visibility, legacy schema preservation, SQL constraints, security allowlist, seed failure and test boundaries.

Inspected Git HEAD (not a guarantee of a clean tree): `c27a55959101e6c29d0fb201c6d6b0d322fd40d1`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java`
- `backend/src/main/java/com/aurorabakery/catalog/api/ProductController.java`
- `backend/src/main/java/com/aurorabakery/catalog/infrastructure/ProductRepository.java`
- `backend/src/main/java/com/aurorabakery/catalog/domain/Product.java`
- `backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java`
- `backend/src/main/java/com/aurorabakery/configuration/ApiExceptionHandler.java`
- `backend/src/main/java/com/aurorabakery/configuration/DevelopmentSeedConfiguration.java`
- `backend/src/main/resources/application.yml`
- `backend/src/main/resources/application-dev.yml`
- `backend/src/main/resources/db/migration/V1__create_stores.sql`
- `backend/src/main/resources/db/migration/V2__single_bakery_catalog.sql`
- `backend/src/test/java/com/aurorabakery/catalog/ProductApiTest.java`
- `backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java`

## Category review in this pass

- [database/catalog-and-transition.md](../database/catalog-and-transition.md)
- [security/read-api-boundaries.md](../security/read-api-boundaries.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Inspect Angular flows, build/Compose/existing-volume configuration, remaining DTO/seed test bodies, ENV and ADR/operations guides; revalidate every retained legacy answer.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
