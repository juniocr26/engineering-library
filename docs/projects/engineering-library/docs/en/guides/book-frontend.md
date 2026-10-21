# Book frontend and catalog

[Project index](../index.md) · [Português brasileiro](../../pt-BR/guides/book-frontend.md)

The landing page implements the approved HTML book prototype: two pages on desktop, a single parchment page at 920px and below, and a cropped illustration above the project list. CSS tokens and textures are in `frontend/app/globals.css`. The supplied writer artwork and EL wax seal live in `frontend/public/assets/`; `app/icon.png` supplies the framework icon. The visual reference is not embedded as a page background. The title uses the locally bundled Great Vibes font under the accompanying SIL Open Font License.

## Responsibilities

- `app/page.tsx` requests the Rails catalog on the server. `app/projects/[slug]/page.tsx` discovers the bilingual Markdown collection through `lib/documentation.ts`; document links open the internal `/projects/[slug]/docs/[...document]` reader route.
- `components/book-layout.tsx`, `project-list.tsx`, `pagination.tsx` and `catalog-state.tsx` own the book, cards, navigation and localized empty/error/loading states. `document-language.tsx` updates the document language after navigation; the initial shell defaults to Portuguese.
- `lib/i18n.ts` defines the two languages and navigation URLs. `lib/pagination.ts` computes bounded page indicators independently of rendering. `lib/catalog.ts` contains typed server-only API access, using the existing `BACKEND_URL`.
- Rails `Catalog::Files` reads only scoped catalog files. `Catalog::Sync` indexes identities. `Catalog::Page` performs PostgreSQL counting, sorting, offset and limit. `Catalog::Presenter` reads localized descriptions for the selected records. `Api::ProjectsController` handles HTTP responses.

## Markdown metadata

Every project has `bio/en.md`, `bio/pt-BR.md` and `bio/icon.svg`. All six catalog projects are covered. Both bios use this format:

```markdown
---
id: stable-project-identifier
name: Canonical Project Name
---

Concise localized description of the verified project purpose.
```

Keep `id` immutable when renaming a directory. Both files must agree on `id` and canonical `name`. The remaining body is a plain-text compact description, not rendered Markdown. Invalid or missing bios abort synchronization before any database write and report the project slug. Preserve identifiers to avoid creating a replacement identity. Conflicting renames fail transactionally rather than overwriting another record. Missing projects are marked inactive, never deleted. Restoring their stable identifier reactivates them. Do not run synchronization while editing catalog files; the database write transaction is serialized, but filesystem discovery is not a filesystem snapshot.


Use the directory basename as the technical slug and set an explicit official human-readable `name` when creating each biography (for example `Env Auditor`, `Go Image Optimizer`, `URL Shortener`). Preserve acronyms and proper names; do not translate the official name between languages. Provide both localized descriptions and `icon.svg`. There is no separate metadata generator. Legacy bios with an absent or blank name use a readable slug fallback with common acronyms preserved; missing bios, invalid IDs and non-string names still fail validation. This fallback does not replace an explicit name. Cards, contents headers, reader headers and bookmark labels use the catalog name; URLs and bookmark associations retain the slug. Run `catalog:sync` after metadata edits to update the existing PostgreSQL row by stable ID, without a schema migration.

Icons are original local SVGs with a 24×24 viewBox, consistent ink strokes and no scripts, external resources or active content. Rails serves them through a scoped endpoint; Next proxies these requests. An unavailable icon uses the local book fallback. The EL seal remains the principal app identity.

## API and pagination

`GET /api/projects?page=2&lang=en` returns `projects` (slug, canonical name, localized description) and `pagination` (page, total_pages, total_projects, page_size). `GET /api/projects/:slug?lang=en` adds existing category indexes. `GET /api/projects/:slug/icon` serves the local SVG. No absolute paths or Markdown documents are returned.

PostgreSQL stores only stable identifier, slug, display name, active flag and timestamps. Bio/icon paths are derived from the slug. Markdown is the source of truth. There is no automatic startup sync: explicitly run `catalog:sync` after catalog changes.

Page size is always five; clients cannot increase it. Ordering is `lower(display_name) COLLATE "C"`, then immutable `stable_id`. This is deterministic case-insensitive byte ordering, not locale-dependent collation. A partial expression index supports active ordering. Invalid, negative, zero, fractional or overlong page parameters select page one; numeric pages beyond the last clamp to the last. Zero projects displays an empty state on page 1 of 1. Exact multiples of five have no extra page.

URL parameters preserve language and page through navigation. Numbered controls include neighbors, endpoints and ellipses, with at most nine indicators. Boundary arrows are disabled. Selected pages have `aria-current`; keyboard focus is visible. Portuguese is the default and the product title is never translated. No runtime translation service is used.

## Development and verification

From the repository root:

```sh
docker compose up -d --build
docker compose exec -T backend bundle exec rails db:prepare catalog:sync
docker compose exec -T -e RAILS_ENV=test backend sh -c 'bundle exec rails db:prepare && bundle exec rails test'
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build:check
python3 -B docs/validation/check_catalog.py
git diff --check
```

Compose mounts documentation at `/docs/projects` (Rails read-only; frontend writable for explicit snapshot generation); Rails uses `CATALOG_ROOT=/docs/projects`. Dependencies stay in images and the frontend uses a `.next` tmpfs. Outside Docker, the catalog defaults to the repository `docs/projects` sibling of Rails; `CATALOG_ROOT` can override it for tests. Tests use the separate Rails test database. Do not run build and the development server concurrently in the same `.next` directory; use `npm run build:check` inside the existing frontend.

Current limits: no documentation editing, authentication or cross-device bookmark synchronization. API downtime produces a localized retry state. The document reader resolves repository Markdown with scoped filesystem reads and preserves project/language navigation.

Browser smoke checks (existing frontend running; browser tooling is included):

```sh
docker compose exec -T frontend node tests/browser.cjs
```

## Reusable manuscript identity

`ManuscriptDecorations` layers original local assets over `.manuscript-surface`, below `.content`. `BookLayout` applies it to the catalog and existing project indexes. The documentation reader reuses this surface with the `reading` composition. The `catalog`, `reading` and `illustration` variants use deterministic content-based layouts from `lib/manuscript.ts`, never `Math.random()`.

Assets live in `frontend/public/assets/manuscript/`: `parchment/` contains the delivered grain WebP and its editable SVG master; `burns/`, `ink/`, `wax/`, `erasures/` and `ornaments/` contain original SVG contours, absorbed ink, amber wax, nonlinguistic crossed pen strokes and the title quill. Reuse these files rather than copying textures. To regenerate the WebP, run Sharp against `aged-fibers-master.svg` with WebP quality 82 from the frontend environment.

Keep strong marks at margins, corners and whitespace. The lighter paper supports text, code and tables; adjust decoration placement for long documents. All decoration is hidden from assistive technology and ignores pointer events; the title remains real text. Preserve focus outlines and contrast. Below 920px the illustration remains in the existing single-page flow; at 480px the feather and edge marks shrink without removing the aged identity. Animations use CSS; no remote images or additional graphics dependency is required. Only the compact WebP is decoded for grain; SVG marks are shared cached assets. The master SVG is an editing source, not loaded by the interface.

## Responsive Table of Contents reader

`documentationEntries` unions canonical relative paths in both languages, sorts categories and filenames using stable case-insensitive canonical ordering, includes README normally and reads localized H1 titles. Missing counterparts are visibly unavailable. Navigation-only indexes are excluded; substantive indexes (including ENV references) remain entries. The frontend uses the `/docs/projects` mount (writable for explicit snapshot maintenance) (`DOCUMENTATION_ROOT`), or defaults to `../docs/projects` outside Docker. PostgreSQL continues to paginate only the project catalog.

Top-level chapter titles (`depth: 0`) use bold weight (700); subsection titles at every depth (`depth > 0`) use normal weight (400). This global rule applies to every catalog project in both languages, across the table of contents, both chapter navigation lists and numbered reader headings. Weight follows the canonical hierarchy from `documentationEntries`, propagated to reader units as `navigationDepth`; it never depends on title text, Markdown heading level or link availability. Title descendants, including nested `strong` elements, inherit that weight. Existing fonts, colors, numbering, layout, links and bold text outside these titles are preserved. Fix rendering styles rather than changing source Markdown to compensate.

Regression: run `docker compose exec -T frontend npm run audit:navigation`, then `docker compose exec -T frontend node tests/chapter-weight.browser.cjs` against the running frontend (`BOOK_READER_URL`, default `http://localhost:3000`). The browser check covers all catalog projects and both languages, chapters 2 and 3, available subsection depths 1–3, both navigation lists and nested emphasis in reader headings.

`BookReader` consumes generic units and a render callback. A hidden, inert container measures actual unit heights and available body height; `ResizeObserver`, font completion and language/content changes trigger repagination. Headings stay with the first child when feasible. Oversized units have an accessible local scroll fallback. Chapter numbers remain independent of physical folios. Resizing anchors the first visible canonical unit where possible; a regrouped page gets a new combined content identity.

A single locked transition lifecycle drives both spread (>920px) and single-page modes. Forward turns rotate the right sheet around its left edge by -180 degrees; backward turns rotate the left sheet around its right edge by +180 degrees. Front/back surfaces, perspective and animated shading share existing textures. Buttons, arrow keys and intentional horizontal swipes navigate. Vertical gestures remain available. Reduced motion changes pages immediately. A timeout recovers interrupted animations. Resize cancels active turns safely.

Decorative seeds combine project, ordered canonical content identities and a versioned variant; translated titles and physical page numbers are excluded. Marks stay stable when that content identity survives reflow. Changed groupings intentionally get a new composition. Burn frames, ink, wax, corrections, liquid rings and abrasions are absolute, pointer-transparent margin layers, independent of measurement. No graphics or animation dependency was added. The existing landing layout and controls remain unchanged; the inspected baseline had no mobile hamburger component, so the TOC supplies a minimal accessible hamburger menu linking back to the catalog.

Limitations: relative references to files outside the documentation collections are unavailable in the reader. Oversized individual units scroll inside their page. Curvature is approximated with lightweight rigid-sheet perspective and shading. Browser visual checks and unit tests are complementary; none prove every document/font/zoom combination.

### Dynamic physical page count

The shared engine displays `Page 1 of N` in single-page mode and `Page 1–2 of N` in spread mode (Portuguese: `Página 1 de N`). The final odd leaf counts once; an empty companion leaf is excluded. The total is the length of the browser-measured page array, never a character estimate or the catalog API total.

Before measurements are available, and while fonts or content images are loading, the controls display `Paginating…` and prevent navigation. The visible leaves show a pagination status until the new measurements are ready. Image load/error, font completion, body/unit resizing, language and content updates trigger measurements. Identical geometry does not rebuild pagination or cancel a turn. The indicator stays on one line to avoid changing the measured page capacity as digits change.

Repagination resolves the canonical reading anchor into the new page array, then aligns it to a spread where appropriate. Physical numbers and totals exist only in browser state; PostgreSQL persists only logical bookmark locations. Bookmarks store canonical content locations independently of these viewport-dependent numbers.

`tests/book-browser.cjs` compares the published total with independently packed DOM measurements, traverses to the last spread, and checks responsive resizing, both languages and changed font metrics. It exercises the table of contents. `tests/document-reader-browser.cjs` exercises actual Markdown routing, chapter/search anchors, Mermaid, bookmark persistence and responsive page navigation.

## Internal Markdown navigation and reader

The previous `documentationEntries` builder hardcoded GitHub blob URLs. There was no document route, Markdown renderer, search or bookmark API to connect. Those were missing functionality, rather than a redirect regression. The builder and Rails category metadata now return internal routes. Catalog project pagination remains unchanged.

`documentationSource` maps canonical IDs (`README` or a localized-relative `.md` path) onto the selected project/language. Each read validates segments and resolves real paths inside the project; invalid, absent or escaping paths produce a parchment-styled 404 without disclosing filesystem locations. Direct URLs, reload and browser history use the Next App Router. Navigation-only index pages remain loadable even when omitted from the TOC. Genuine external HTTP(S)/mail links retain their destinations; Markdown links within collections resolve relative to their actual source path, including language and cross-project links. Source-code references outside collections are shown without a destination rather than pointing at local files. Images use a scoped, extension-allowlisted asset endpoint with restrictive CSP and nosniff.

`markdownUnits` parses a Markdown AST with remark/GFM. Top-level semantic units preserve headings, paragraphs, lists, code, tables and reference definitions. Heading anchors follow GitHub slug conventions; other blocks use a section/content hash, so inserting a different block does not shift their identity. `MarkdownUnit` uses react-markdown with raw HTML disabled. Mermaid is loaded lazily in strict mode, with accessible diagram source and a source-code fallback on failure. Pending diagram rendering participates in measurement readiness. Wide content can scroll locally; an oversized semantic unit remains on one physical page with internal scrolling. Physical page totals count the engine's leaves, not scroll subdivisions.

`DocumentationReader` composes the existing `BookReader`, Markdown units and native-dialog parchment panels. Search, chapters and saved bookmarks have separate controls; each visible leaf has its own bookmark toggle and animated corner ribbon. Dialogs trap focus, restore it on closing and support Escape. Chapter, search and bookmark destinations share the reader route and content anchors. Anchor jumps select the containing measured page; ordinary previous/next turns retain the existing animation. Chapter-boundary controls animate the departing leaf using the shared engine, then load the destination route; destination content is displayed after measurement. Missing/translated anchors display an explicit fallback notice. No page-number equivalence between languages is assumed.

## Search and shared PostgreSQL bookmarks

`GET /api/document-search/:project?q=...&lang=...` scans the selected collection's actual Markdown on demand, matches semantic block text and returns up to 80 contextual results with internal routes and anchors. The UI debounces input, cancels stale requests, and shows loading/empty/error states. There is no separate index to synchronize. The selected result block receives red text highlights. Search skips navigation-only indexes and ignores raw HTML/decorations.

Rails exposes shared bookmark, highlight, note and combined annotation APIs through same-origin Next routes. Data is organized by canonical project, document and required language. GET supplies an expiring signed application CSRF token, without cookies or browser registration; mutations require `X-Annotation-CSRF`. The proxy verifies Origin, forwards the CSRF header and uses `no-store`. There are no accounts, reader profiles or annotation sessions.

Migrations `20261020010000` and `20261020020000` transition existing annotations to shared storage without deleting rows or changing note bodies/foreign keys. A bookmark location uses project, document, language, anchor and a deterministic `location_variant` to preserve legacy duplicates. New repeated bookmark requests reuse the existing location. Notes retain their record IDs and unique optional highlight association, with a non-unique range index so distinct legacy notes at the same passage survive. The API returns 422 for invalid content, 403 for missing/invalid CSRF, 404 for absent or wrongly scoped IDs and 503 for database failures. Physical page numbers are never persisted.

Every browser accessing this installation sees the same saved annotations after opening or refreshing the reader. Changing language selects a separate collection and never copies annotations. Content changes can invalidate a block anchor; the reader reports unavailable positions. No private-document authorization is provided. Demonstration seeding and cleanup are explicit CLI actions; see [development demonstrations](../img/development-demos.md).

Missing documents use Next `notFound()`: the error UI can arrive with HTTP 200 when the ancestor loading boundary has already started streaming; non-streamed responses use 404. Asset endpoints return 404 directly. Reference: [Next not-found](https://nextjs.org/docs/app/api-reference/file-conventions/not-found).

Run the complete reader browser regression with the browser included in the development image:

```sh
docker compose exec -T frontend node tests/document-reader-browser.cjs
```

## Canonical continuous reading navigation

`frontend/lib/reading-order.ts` separates logical document order from physical pagination. `getReadingSequence(project, language, entries)` consumes the same `documentationEntries` metadata rendered by the table of contents. Its first entry has `id: null` and the internal contents URL; subsequent entries retain the TOC's stable document IDs and internal localized URLs. Category headings and unavailable translations have no URL and are excluded. Navigation-only indexes are already excluded by the catalog; substantive indexes remain eligible. No translated-title sorting or separate navigation manifest exists. Adding readable Markdown to the existing collection automatically adds it in the canonical TOC position. Corresponding documents retain the same relative order across languages, with unavailable translations skipped.

`getPreviousDocument`, `getNextDocument`, `getFirstDocument` and `getLastDocument` query that sequence. Unknown IDs have no neighbors; an empty collection has only its contents entry. `readingNeighbors` converts the adjacent entries into route intents. Forward destinations open at the beginning. Backward destinations carry `edge=end`; the destination resolves its last physical page only after fonts, images, diagrams and viewport geometry have been measured. Counts remain scoped to each document and are never copied from the departing reader or persisted in PostgreSQL.

`TableOfContents` and `DocumentationReader` pass these intents to the existing `BookReader`. Ordinary arrows still turn physical pages. At a logical boundary the appropriate arrow is replaced by an accessible bar-and-arrow chapter control, including contents ↔ first document. The final document has no forward destination and does not wrap. Clicks, arrow keys and swipes share the same navigation lock and directional animation; reduced motion skips animation. Neighbor routes are prefetched. The outgoing animation uses the departing document's leaves; it does not attempt to render the unloaded destination on the back of the sheet. The route then shows a pagination status until its own measurements are available.

App Router maintains browser route history. The current history entry also retains the logical page anchor, while preserving Next's history fields; returning resolves that anchor against current geometry. Resizing preserves the logical anchor rather than a stale physical number. Direct document URLs start at the beginning unless an explicit anchor or ending intent is supplied. Files removed after catalog discovery retain the existing internal not-found recovery; missing localized entries discovered initially never become destinations.

Resolver cases are covered by `tests/reading-order.test.ts`; `tests/continuous-reading.browser.cjs` exercises both directions, category boundaries, direct routes, last-document termination, destination indicators, browser history, responsive layouts and reduced motion against the actual collection. Run it with the same container browser as the reader regression above.
