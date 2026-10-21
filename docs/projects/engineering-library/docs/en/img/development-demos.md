# Development demonstrations

Engineering Library uses one shared local PostgreSQL annotation dataset, organized by project, document and language, without accounts, sessions or reader profiles. Run the seed command once, then open or refresh any browser accessing the same installation. No enrollment, special cookie or browser action is required. An empty database shows empty collections.

Docker startup initializes catalog metadata only. Seeding and cleanup are optional, explicit development commands and never run at boot or in production. Do not reset PostgreSQL or remove its volume.

## Commands

From the host shell at the repository root, start the services (startup applies migrations). Playwright and Chromium are included in the development image:

```sh
# Run from the repository root on the host shell.
docker compose up -d --build --wait --wait-timeout 300
docker compose exec -T frontend npm run notes:demos
docker compose exec -T frontend npm run notes:demos:verify
docker compose exec -T frontend npm run notes:demos:manifest
```

`PLAYWRIGHT_EXECUTABLE_PATH` may select an installed browser. The CLI launches a disposable browser only to measure real document anchors; it stores no persistent browser profile and all writes use the shared APIs. `notes:demos` reconciles explicit `demo_key` records without duplicates. It never adopts or overwrites a manual note/bookmark at a conflicting passage; a conflict is reported, and an interrupted run may leave a partial seed. Resolve the conflict and rerun explicitly.

`notes:demos:verify` reads the shared dataset through a fresh browser and opens real indicators/previews. `notes:demos:manifest` is read-only and writes `/tmp/engineering-note-demo-manifest.json` with navigable record URLs and valid/invalid anchor flags. It does not seed or delete data. Reconcile demonstrations explicitly after changing source documents; invalid annotations are never shown on unrelated text.

## Open the normal reader

- [architecture/current-state.md · en](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=en)
- [architecture/current-state.md · pt-BR](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=pt-BR)
- [img/visual-components.md · en](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=en)
- [img/visual-components.md · pt-BR](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=pt-BR)

Open **Highlights and Notes** and **My Bookmarks**, navigate to a saved passage and click its superscript note indicator. Page ribbons and highlight colors use the same persisted data. Opening a second independent browser or refreshing restores the same collection. Changes in one browser appear in another after refresh; there is no live push synchronization. English and Portuguese remain strictly independent and are never copied between languages.

## Expected counts

Each document/language has 15 notes, 15 active highlights (14 with notes plus one independent highlight) and 3 bookmarks. Across both documents and languages: **60 notes, 60 highlights and 12 bookmarks**. Four notes have no color. Per language, the project panel has 32 combined annotations, including 30 notes: yellow 6, each of the other six colors 4. Initial pagination loads 20 entries. The seed creates 76 scenarios and the baseline manifest validates 132 persisted anchors. Manual annotations and preserved legacy duplicates may increase totals; they are not removed to force fixture counts.

DBeaver uses the existing `localhost:5499` connection and local credentials, database `engineering_library`. Read-only diagnostics:

```sql
SELECT language, document, count(*) FROM notes
WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

## Explicit cleanup

Run separately only when you want to remove the shared demonstrations:

```sh
docker compose exec -T frontend npm run notes:demos:cleanup
```

Cleanup removes only tagged demonstration records throughout the Engineering Library project, in both documents and languages. Manual notes, highlights and bookmarks remain. If a manual note references a demonstration highlight, deleting that highlight nullifies the relationship and preserves its independently anchored Markdown. Every browser reflects cleanup after refresh. No browser identity is involved. Do not run seed and cleanup concurrently.

## Migration and regression tests

See [shared migration](../architecture/current-state.md#shared-annotation-migration) for legacy duplicate preservation. The transition adds shared indexes before dropping obsolete ownership; it retains IDs, distinct note bodies and relationships. Rollback requires a reviewed backup because removed ownership cannot be reconstructed.

`test:demos:browser` requires an explicitly isolated QA installation (`SHARED_ANNOTATIONS_TEST=1` and `BROWSER_BASE_URL`), refuses nonempty annotation collections before destructive fixture checks, and verifies shared CRUD, two independent browser contexts, language filtering, seed idempotency and demonstration-only cleanup. Rails tests also exercise conflicting legacy rows in a temporary PostgreSQL schema. Ordinary application startup never invokes these tests.

The frontend must be running for setup and cleanup. The manifest stays inside the container; copy it with `docker compose cp frontend:/tmp/engineering-note-demo-manifest.json /tmp/engineering-note-demo-manifest.json`. Its URLs use internal port 3000; replace the origin with `http://localhost:3099` to open them on the host.

## Test database / Banco de testes

```sh
docker compose exec -T -e RAILS_ENV=test backend sh -c 'bin/rails db:prepare && bin/rails test test/integration/note_demos_api_test.rb'
```

This test creates synthetic demonstrations and manual annotations in the existing PostgreSQL database with the `_test` suffix. It verifies idempotency and preservation of manual notes, highlights and bookmarks after demonstration cleanup.

For the complete CLI/browser regression, reuse the same three services. The commands below create only a temporary database in the existing PostgreSQL and recreate the existing backend to point to it. The frontend keeps using `http://backend:3000`; there is no additional server or reader profile. Requires all three services running, PostgreSQL role permission to create a database and no other process editing annotations during the test: browsers temporarily see the synthetic dataset. The trap restores the original configuration on failure; the temporary database then remains for inspection. On success, only that temporary database is removed. Do not change `.env` during this procedure or run the suite directly against the shared database.

```sh
(
  set -eu
  LIBRARY_QA_DB="engineering_library_workflow_check_$(date +%s)"
  restore_backend() {
    docker compose up -d --no-deps --wait --wait-timeout 300 backend
  }
  trap restore_backend EXIT
  docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" "$1"' sh "$LIBRARY_QA_DB"
  POSTGRES_DB="$LIBRARY_QA_DB" docker compose up -d --no-deps --wait --wait-timeout 300 backend
  docker compose exec -T -e SHARED_ANNOTATIONS_TEST=1 frontend npm run test:demos:browser
  restore_backend
  trap - EXIT
  docker compose exec -T postgres sh -c 'dropdb -U "$POSTGRES_USER" "$1"' sh "$LIBRARY_QA_DB"
)
```
