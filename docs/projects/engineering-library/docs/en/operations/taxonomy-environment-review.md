# Implementation review — 2026-10-18

26 files migrated from `technical-interview/` to `faq/` across six projects and two languages. HEAD comparison confirmed preserved question headings and content, allowing only category naming and repaired links. Twelve bilingual ENV references now describe Compose interpolation and direct runtime behavior; env-auditor explicitly has no application-specific runtime schema. Sources for all six projects were locally available. Unknown framework/image behavior is identified rather than assigned invented defaults.

Engineering Library guides were recovered from `bed78d2` directly into this project collection. Root language directories were not recreated. Root/component/project READMEs, library/language/category indexes, import destinations, affected links, Compose, environment defaults and validation tooling were updated. New files include the root MIT LICENSE, five catalog regression tests, bilingual migration procedures and this report. Existing historical hashes and evidence remain historical.

Host defaults are Next 3099 → 3000, Rails 3098 → 3000 and PostgreSQL 5499 → 5432, all on loopback. The ports were available before changes. Rails uses `postgres:5432`, and Next fetches `http://backend:3000` server-side, requiring no CORS change. Existing `database.yml` already consumes POSTGRES_DB.

After explicit owner approval, both development/test databases were backed up in custom format, roles were backed up, archive catalogs were validated and applications briefly stopped. SQL renamed the databases to `engineering_library` and `engineering_library_test`; queries verified final names and the preserved development metadata row. No domain tables, slots or prepared transactions were found. Development subscriptions were also checked and absent. Existing PostgreSQL 18 physical storage was preserved without cluster reinitialization or deletion. Private backups remain in ignored `.local-backups/2026-10-18-database-rename/` with restricted permissions. Credentials were preserved. See [migration and recovery](database-migration.md).

MIT copyright 2026 Júnio César Rosa is supported by Git authorship and the five source projects' matching MIT licenses. No conflicting root license was present. Third-party dependencies retain their licenses. Keep private documents in separate repositories with access controls and secret management; public licensing does not make private material safe to publish.

Validation executed:

- `python3 -B docs/validation/check_catalog.py`: no errors or warnings; bilingual paths, FAQ/ENV references, links, anchors and navigation checked.
- `python3 -B -m unittest discover -s tools -p 'test_*.py' -v`: 27 passed, including five new catalog regressions.
- `docker compose config --quiet`, `docker compose up -d`, `docker compose ps`: valid configuration and three healthy services on new ports.
- `docker compose exec -T backend bin/rails test`: two tests, four assertions, no failures/errors/skips.
- Host HTTP requests: Rails 3098/up and Next 3099 returned 200.
- Host PostgreSQL 5499 responded to protocol negotiation; SQL checked renamed databases, metadata and storage version 18.
- `pg_restore --list`: both private backup catalogs readable.
- `git diff --check`: clean. Environment, backups and data remain ignored/untracked; nothing staged, committed or pushed.

Limits: DBeaver was not run; protocol connectivity is not an authenticated DBeaver session. No full backup restore drill was performed. External URLs were not fetched; structural checks do not certify translation or external framework/image behavior. Legacy workspace manifest/tooling remains available, but current catalog verification uses the project catalog checker above.

Suggested Conventional Commit:

```text
feat(docs): standardize FAQ and env catalogs and update development infrastructure
```
