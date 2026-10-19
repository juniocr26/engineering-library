# Documentation audit — 2026-10-19

[Project index](../index.md) · [Technical FAQ](../faq/index.md) · [Português brasileiro](../../pt-BR/operations/documentation-audit-2026-10-19.md)

**Status: partial; the complete portfolio audit remains open.** This bounded pass makes full existing FAQ answers available directly in the category index, preserves study-guide paths/anchors, and adds current source-grounded corrections. Retained historical answers have not all been revalidated line by line.

## Historical recovery

Commit `5052a8515b30278abea5fb81b37647482c10ba18` exists in Engineering Library. Its `docs/en/interviews/` and `docs/pt-BR/interviews/` contain all six project guides and foundations. The current study guides already preserve the project material, with relocated links/status notes. No checkout/reset or old directory restoration was performed. Foundations were selectively rewritten in the Library FAQ to remove obsolete worker-absence claims and avoid private-product references.

## Current evidence and corrections

Creation/resolution path, Redis initialization, Cassandra upsert, cross-store uncertainty, global encoding settings and selected fake-backed tests.

Inspected Git HEAD (not a guarantee of a clean tree): `ed43c65c2893172f94c231ee608ecf2753b8f92f`.

The following are source paths, not instructions to execute them. Large files were inspected selectively; file hashes in the machine record identify inputs without claiming every line was reviewed.

- `app/main.py`
- `app/schemas.py`
- `app/api/routes.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/services/url_service.py`
- `app/infrastructure/redis_id_generator.py`
- `app/infrastructure/cassandra_url_store.py`
- `app/helpers/base62.py`
- `app/helpers/obfuscation.py`
- `tests/test_redis_id_generator.py`
- `tests/test_url_service.py`

## Category review in this pass

- [architecture/overview.md](../architecture/overview.md)
- [database/identity-and-consistency.md](../database/identity-and-consistency.md)

Both languages received current FAQ answers and category corrections. Legacy wording and historical test results remain dated evidence. Path/Q-ID parity is structural, not a full translation certification.

## Validation and remaining work

Executed: `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` in Engineering Library: 27 passed. The final current catalog check passed with 442 Markdown files, 3,540 local links, zero errors and zero warnings; `git diff --check` passed. These are structural checks, not browser or semantic certification. Host `node --version` and `npm --version` both failed because the commands are unavailable. No installation, service startup, sibling suite, browser check, stage, commit or push was performed.

Inspect controllers/dependency injection, all test bodies, Cassandra bootstrap/consistency and Compose/AOF configuration, ENV, security/operations guides; revalidate every retained legacy answer.

[Resumable portfolio record](../../../../../validation/documentation-audit-2026-10-19.json) lists source hashes, remaining document paths and limits. Resume with pending implementation paths and compare both languages; do not mark the repository fully audited from this pass.
