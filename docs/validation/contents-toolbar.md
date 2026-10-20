# Table of contents reader tools

The table of contents and documentation now share `ReaderTools`: the original
icons, search, chapter list, shared bookmark requests, panel and ribbon lifecycle
were extracted from `DocumentationReader`. `BookReader` remains the only pagination
and page-turning engine.

## Bookmark contract

`document: "@contents"` identifies the virtual table of contents. `anchor` stores
the first canonical `TocEntry.id` on the selected physical leaf, including category
IDs such as `category:architecture`. Language remains part of bookmark identity.
No database migration, account or second bookmark store is needed. Rails accepts
this reserved document only after validating the active project and language;
application CSRF, shared location uniqueness, limits and project/language filtering apply.

Bookmark links route to `/projects/:slug?lang=:language#encoded-entry-id` rather
than `/docs/`. The shared reader resolves the anchor against newly measured pages.
Language links retain the current logical position; responsive reflow uses the
reader's existing anchor. If several saved anchors end up on one physical leaf,
the ribbon removes one matching bookmark at a time, as in the document reader.
Removed entries cannot be restored after a content change.

## Layout

The existing toolbar is inserted into the contents header. Both the visible left
header and its measurement probe contain the same controls. The right leaf uses
the existing standalone control reservation. Header wrapping therefore participates
in measured pagination without hardcoded page totals or changes to parchment CSS.

## Reproducible checks

Use the existing Docker Compose development services:

```sh
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm test
docker compose exec -T backend bin/rails test
```

Browser checks require an externally supplied Playwright installation (no new app
dependency): set `PLAYWRIGHT_MODULE` to its module path and `BROWSER_BASE_URL` to the
running frontend, then run:

- `node tests/contents-toolbar.browser.cjs`: four viewport widths, real search and
  internal result navigation, chapter panel, mocked bookmark API, logical anchor
  restoration, language switching, overflow and measured control clearance.
- `node tests/contents-persistence.browser.cjs`: shared Rails/PostgreSQL
  create, independent desktop leaves, reload and ribbon deletion, using an isolated
  QA installation and cleaning only the exact fixture IDs afterward.
- `node tests/bookmark-controls.browser.cjs`: existing document control regression.

## Validation executed (2026-10-19)

- TypeScript and ESLint: passed.
- Frontend unit suite: 37 passed.
- Rails full suite: 14 tests, 245 assertions, zero failures/errors/skips.
- Contents toolbar browser checks: passed at 1440, 768, 390 and 320 px.
- Real Rails/PostgreSQL persistence browser check: passed.
- Existing document bookmark control browser checks: passed at all four widths,
  including API failure handling, ribbon transitions and reduced motion.
- Existing book reader browser checks: passed at 390, 768 and 1440 px.
- Continuous reading: passed at 390, 768 and 1440 px in both languages,
  including reduced motion at 768 px. Its resize assertion now waits for the new
  reader mode before checking controls, matching asynchronous measurement.
- Production build: passed in a temporary source copy inside the frontend container
  with the existing dependency installation, leaving the dev server cache intact.
- Visual inspection: Chromium desktop and mobile screenshots checked.
- `git diff --check`: passed. No staging, commit or push performed.

Browser coverage uses Chromium; Safari and Firefox were not run. Logical anchors
cannot restore content that has been removed from the canonical table of contents.
