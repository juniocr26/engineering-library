# Book frontend and catalog

[Project index](../index.md) · [Português brasileiro](../../pt-BR/guides/book-frontend.md)

The landing page implements the approved HTML book prototype: two pages on desktop, a single parchment page at 920px and below, and a cropped illustration above the project list. CSS tokens and textures are in `frontend/app/globals.css`. The supplied writer artwork and EL wax seal live in `frontend/public/assets/`; `app/icon.png` supplies the framework icon. The visual reference is not embedded as a page background. The title uses the locally bundled Great Vibes font under the accompanying SIL Open Font License.

## Responsibilities

- `app/page.tsx` requests the Rails catalog on the server. `app/projects/[slug]/page.tsx` displays real category indexes; links open public repository Markdown, pending a future reader.
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
docker compose exec -T backend sh -c 'RAILS_ENV=test bundle exec rails db:prepare && bundle exec rails test'
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
python3 -B docs/validation/check_catalog.py
git diff --check
```

Compose adds only a read-only documentation mount at `/docs/projects`; existing database configuration and environment remain intact. Outside Docker, the catalog defaults to the repository `docs/projects` sibling of Rails; `CATALOG_ROOT` can override it for tests. Tests use the separate Rails test database. Do not run build and the development server concurrently in the same `.next` directory; stop development or use a separate build output directory.

Current limits: no full document reader, editing, bookmarks, page-turning animation, authentication or search. API downtime produces a localized retry state. Future reader work must resolve document links safely, render Markdown accessibly and preserve project/language/category navigation.

Browser smoke checks (install Playwright and Chromium in a temporary directory first):

```sh
# Run a production server on port 3100 after building.
docker compose exec -T frontend npm run start -- --port 3100
# In another terminal, with the external Playwright module path:
docker compose exec -T frontend sh -c 'PLAYWRIGHT_MODULE=/tmp/el-browser/node_modules/playwright node tests/browser.cjs'
```

## Reusable manuscript identity

`ManuscriptDecorations` layers original local assets over `.manuscript-surface`, below `.content`. `BookLayout` applies it to the catalog and existing project indexes. Future readers, FAQ and documentation pages should reuse this surface and select the `reading` composition; those future screens are not implemented here. The `catalog`, `reading` and `illustration` variants use fixed CSS placements, never runtime randomness.

Assets live in `frontend/public/assets/manuscript/`: `parchment/` contains the delivered grain WebP and its editable SVG master; `burns/`, `ink/`, `wax/`, `erasures/` and `ornaments/` contain original SVG contours, absorbed ink, amber wax, nonlinguistic crossed pen strokes and the title quill. Reuse these files rather than copying textures. To regenerate the WebP, run Sharp against `aged-fibers-master.svg` with WebP quality 82 from the frontend environment.

Keep strong marks at margins, corners and whitespace. The lighter paper supports text, code and tables; adjust decoration placement for long documents. All decoration is hidden from assistive technology and ignores pointer events; the title remains real text. Preserve focus outlines and contrast. Below 920px the illustration remains in the existing single-page flow; at 480px the feather and edge marks shrink without removing the aged identity. No animation, remote images or additional graphics dependency is required. Only the compact WebP is decoded for grain; SVG marks are shared cached assets. The master SVG is an editing source, not loaded by the interface.
