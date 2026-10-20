# Development demonstrations

Explicit commands; never run at boot or in production. Do not use db:reset. Install Playwright first; set PLAYWRIGHT_MODULE if needed.

```sh
docker compose exec backend bin/rails db:migrate
cd frontend
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:verify
npm run notes:demos:manifest
```

For your browser, open architecture/current-state.md and img/visual-components.md with ?lang=en&noteDemos=1. Open Development note demonstrations and click Seed current reader for each document and language. Download manifest supplies note links. The script uses a separate persistent local profile with a random Rails-signed cookie. Do not copy cookie secrets.

In DBeaver use the existing local connection on localhost:5499 with local environment database and credentials. Do not disclose reader_digest. These read-only queries count all demonstration owners; the reader only displays its cookie.

```sql
SELECT language, document, count(*) FROM notes
WHERE demo_key IS NOT NULL GROUP BY language, document;
SELECT language, color, count(*) FROM highlights
WHERE demo_key IS NOT NULL GROUP BY language, color;
SELECT language, document, count(*) FROM bookmarks
WHERE demo_key IS NOT NULL GROUP BY language, document;
```

Seeds create Markdown notes, seven colors, a colorless note, a highlight without a note and beginning/middle/end bookmarks across two documents and both languages. Anchors derive from the actual measurement DOM. Cleanup is explicit and scoped to project and owner using demo_key, never body prefixes. Existing notes at the same passage cause a conflict instead of being adopted. Static content works without the database. Open manifest links, click the note indicator, preview and expand tables/images/diagrams. Inspect filters, ribbons, language and pagination at your viewport.


## Playwright

```sh
npm install --prefix /tmp/engineering-library-browser playwright
export PLAYWRIGHT_MODULE=/tmp/engineering-library-browser/node_modules/playwright
/tmp/engineering-library-browser/node_modules/.bin/playwright install chromium
# Optional: PLAYWRIGHT_EXECUTABLE_PATH=/path/to/installed/browser
# Optional: DEMO_BROWSER_PROFILE=/tmp/engineering-note-demo-browser
```

Run npm commands on a host with Node.js and Compose available. The fixture profile persists, but its initial cookie is random and protected. Do not run two commands against the same profile concurrently. The manifest command reads the last exported JSON; verification queries persisted data through the API and opens actual indicators. For static validation without seeds: `node tests/visual-catalog.browser.cjs` from frontend, with the same Playwright variables.

Matrix per document and language: 15 notes, 15 active highlights (14 with notes and one without) and 3 bookmarks. Expected fixture totals across two documents and languages: 60 notes, 60 highlights, 12 bookmarks. Four notes retain no color. The manifest lists 76 scenarios, including notes and independent records. Note bodies include Unicode, headings, lists, checklists, a small table, a wide 35-row table, code, images and Mermaid. The long note combines resources. Some synthetic technical descriptions and identifiers remain in English.

Cleanup removes this owner's demonstrations throughout the selected project in both languages. It never runs automatically. It may preserve colors from legacy demonstrations without explicit highlight ownership instead of risking removal of personal highlights.


## Validation on 2026-10-20

Executed: 94 frontend tests, 24 Rails tests (412 assertions), 27 Python tests, typecheck and lint. Edge opened all 60 persisted notes and checked seven colors, four colorless notes, wide/long tables, Mermaid and note images. Repeated seeding retained 60 notes, 60 highlights and 12 bookmarks; read-only verification after restarting Rails passed without recreating data. Explicit cleanup of a temporary profile preserved the fixture profile; the Rails test also preserved personal records and another reader's data.

Without seeds, the contents discovered IMG; local JPEG, local SVG, HTTPS SVG and HTTPS GIF loaded with real dimensions; the invalid URL showed the fallback. Mermaid flowchart and sequence diagrams rendered, and fullscreen, zoom and pan were exercised. The annotation suite passed at 1440px and 390px. Firefox and Safari were not executed. External media remains dependent on its provider.

The catalog validator checked 451 Markdown files and 3559 local links. Two earlier documents remain unreachable from the central index: validation/heading-numbering.md and validation/navigation-audit.md; IMG files introduce no validation errors.

Optional cleanup, as a separate invocation, only when you want to remove demonstrations:

```sh
BROWSER_BASE_URL=http://localhost:3099 npm run notes:demos:cleanup
```
