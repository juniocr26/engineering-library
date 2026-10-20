# Development demonstrations

Docker startup (`docker compose up -d --build`) initializes catalog metadata, not annotation demonstrations. A fresh anonymous reader has empty collections. Demonstrations are optional, development-only, manual actions; cleanup never runs automatically. Do not reset PostgreSQL or remove its volume.

## Workflow A — CLI demonstration reader

The CLI uses a dedicated persistent browser profile, by default `/tmp/engineering-note-demo-browser` (override with `DEMO_BROWSER_PROFILE`). Rails creates its random signed HttpOnly `engineering_reader` cookie through the normal bookmarks API. PostgreSQL stores only its SHA-256 digest. These records belong to that profile; running verification or opening a manifest link in a different browser does not transfer their ownership. A non-null `demo_key` identifies cleanup ownership, not public visibility. Never copy cookies or publish digests.

With Node.js and Playwright installed on the host:

```sh
cd frontend
npm install --prefix /tmp/engineering-library-browser playwright
export PLAYWRIGHT_MODULE=/tmp/engineering-library-browser/node_modules/playwright
/tmp/engineering-library-browser/node_modules/.bin/playwright install chromium
export BROWSER_BASE_URL=http://localhost:3099
npm run notes:demos
npm run notes:demos:verify
npm run notes:demos:manifest
```

Set `PLAYWRIGHT_EXECUTABLE_PATH` to use an installed browser. Do not run commands concurrently against the same profile. `notes:demos` seeds or reconciles this profile only. `notes:demos:verify` reads persisted records and opens actual note indicators and previews. `notes:demos:manifest` performs read-only live anchor diagnostics; it never seeds or deletes records. It writes `/tmp/engineering-note-demo-manifest.json` with record IDs, document/language, logical anchors and `valid` flags plus valid/invalid totals, without cookie secrets or digests. After document edits, inspect invalid anchors and explicitly rerun seeding to reconcile demonstration anchors. User-created records are preserved.

## Workflow B — current browser demonstrations

Use the browser where you want the annotations to appear, consistently on `localhost:3099`. A separate browser, private window, profile, or `127.0.0.1` hostname may have a different identity.

1. Open each of these four URLs:
   - [Architecture, English](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=en&noteDemos=1)
   - [Visual components, English](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=en&noteDemos=1)
   - [Arquitetura, português](http://localhost:3099/projects/engineering-library/docs/architecture/current-state.md?lang=pt-BR&noteDemos=1)
   - [Componentes visuais, português](http://localhost:3099/projects/engineering-library/docs/img/visual-components.md?lang=pt-BR&noteDemos=1)
2. Expand **Development note demonstrations** below the book, scrolling if necessary. Click **Seed current reader** once on each URL. This action populates only the open document and language, using your existing protected cookie. It does not adopt the CLI identity. Other documents show guidance links instead of an enabled seed button.
3. Wait for the saved-count status. Notes and highlights refresh immediately; bookmark panels and page ribbons refresh too. Open **Highlights and Notes** and **My Bookmarks** in the normal toolbar. Use the filters or the generated passage links and click the superscript note indicator. **Download manifest** exports the passages created in this document; use the CLI read-only manifest for validation of its separate profile.
4. Remove `noteDemos=1` or reload normally. The same browser keeps its data. Switch language to see that language's independent collection. No Docker restart is needed.

Repeating the action reconciles demonstrations without duplicates. A personal note or bookmark occupying the target passage causes a conflict, rather than being overwritten. An interrupted run may leave partial demonstrations; the error is displayed and saved state is refreshed. Resolve the conflict or use an empty development browser profile before retrying. Personal data is never removed to make room.

## Counts and database inspection

Per document and language: 15 notes, 15 active highlights (14 with notes and one independent highlight), 3 bookmarks. Two documents and two languages give **60 notes, 60 highlights, 12 bookmarks per seeded reader**. Four notes have no color. Per language the project panel has 32 annotations, including 30 notes: yellow 6; blue, pink, orange, purple, red and green 4 each. The panel initially loads 20 entries; use its load-more control for the remainder. The seed manifest contains 76 creation scenarios; live validation checks 132 persisted anchors.

The two canonical document identities are `architecture/current-state.md` and `img/visual-components.md`, independent of language. Actual text anchors derive from the reader's measured DOM. The normal notes/highlights API is document-scoped; `/api/annotations?project=engineering-library&language=en` and `/api/bookmarks?project_slug=engineering-library&language=en` are project-wide. Every read remains cookie-owner and language scoped, with `no-store` caching.

DBeaver connects to `localhost:5499`, database `engineering_library`, with your existing local credentials. These read-only queries aggregate **all** demo readers, not just the browser you have open. Two fully seeded identities double the totals. Row counts alone do not establish browser visibility.

```sql
SELECT language, document, count(*), count(DISTINCT reader_digest) AS owners
FROM notes WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

## Explicit cleanup

In the development interface, **Remove demonstration records** removes only the current browser's tagged demonstrations throughout this project, across both documents and languages, then refreshes the UI. It preserves personal records and other readers. It is not limited to the document shown.

For the CLI fixture only, run this separately when removal is intended:

```sh
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:cleanup
```

Use the same `DEMO_BROWSER_PROFILE` as the seed. This does not clean your normal browser. Legacy colors without explicit demo ownership may remain to avoid deleting personal highlights.

## Validation on 2026-10-20 — visibility correction

The fresh temporary Edge reader started empty despite the existing CLI fixture. The explicit UI action passed in both documents and languages: immediate note indicators, ribbons and project bookmark lists, repeated seeding, all seven filter counts, notes filter, reload, isolation of another fresh reader, and explicit cleanup of the temporary owner. Run `npm run test:demos:browser` with the Playwright environment above. Rails regression coverage checks moved-anchor reconciliation, idempotency, owner isolation and cleanup preservation. See the task report for actual suite results and preview validation; this guide does not infer the identity of an already-open user browser. Firefox and Safari require separate validation; remote media depends on provider availability.
