# Engineering Library: current architecture

Static source review: 2026-10-19. This page describes the current working tree; historical scaffold descriptions are superseded. [Book frontend and catalog](../guides/book-frontend.md) describes the reader in greater detail.

## Purpose and evidence boundary

The Library maintains bilingual engineering explanations, project FAQs and source evidence. Markdown in `docs/projects/` owns document bodies and bios. Rails serves catalog metadata and shared annotations; Next.js renders the internal book reader. Source and test definitions were inspected, without starting services or executing database-backed tests. No production deployment, measured capacity or AI agent is established.

## Implemented foundation

`backend/config/routes.rb` exposes `GET /api/projects`, `GET /api/projects/:id`, the project icon endpoint, bookmark list/create/delete and `/up`. `CatalogProject` and `Bookmark` have real PostgreSQL schema, validations and indexes. `/up` indicates Rails boot health; it does not query the catalog or certify PostgreSQL readiness.

`Catalog::Sync` scans catalog directories, validates localized bio identity/name agreement and duplicate stable IDs before writes. A transaction-scoped advisory lock serializes database updates; records are matched by `stable_id`, renamed by slug and deactivated when absent. Unchanged records avoid writes. Validation failure retains the last valid database index. The transaction does not snapshot files: keep catalog files stable while synchronizing. Markdown document edits do not require database ingestion; metadata edits need explicit `catalog:sync`.

`Catalog::Page` selects active records with fixed page size five and deterministic `lower(display_name) COLLATE "C", stable_id` order. Offset pagination is simple and index-supported but is not a snapshot across requests during catalog changes. Next fetches catalog JSON server-side with `cache: 'no-store'` and a five-second timeout. Its collection filesystem reader is separate from the Rails metadata API.

`compose.yaml` defines PostgreSQL, Rails and Next. Ports bind to loopback. PostgreSQL data uses `.dockerized-postgres` on the host; this is persistence, not a verified backup. Both application services receive the documentation collection read-only. Dependency/build directories remain development bind mounts. Startup health dependencies do not implement automatic application-level recovery after every dependency failure.

## Responsibilities and trade-offs

Rails owns indexed metadata, catalog pagination and bookmark persistence. Next owns Markdown rendering, logical document order and browser-measured physical pagination. Filesystem content and database metadata are different consistency boundaries. `Catalog::Files.read` resolves real paths within a validated project; `collectionFile` applies its own scoped checks on the Next side. Neither check is a race-free adversarial filesystem sandbox.

Engineering Library uses one shared local PostgreSQL annotation dataset, organized by project, document and language, without accounts, sessions or reader profiles. Independent browsers read and mutate the same annotations. GET returns an expiring application CSRF token; mutations require `X-Annotation-CSRF`, and the Next proxy verifies Origin. Language remains mandatory. Logical anchors are independent of physical pages; their existence is checked when navigating, with an explicit unavailable-location fallback.

## Catalog contract

Navigation is Library → Project → Language → Category → Document. `documentationEntries` merges relative IDs across both languages, sorts deterministically, excludes navigation-only indexes and retains substantive ones. Missing translations have no destination. `reading-order.ts` derives neighboring document routes from those same entries. Physical page counts depend on fonts, diagrams, images and viewport measurements; URLs/bookmarks retain logical document/anchor identities instead of physical page numbers.

Technical FAQ answers live directly in `faq/index.md`. Existing `study-guide.md` paths and heading anchors remain compatibility references. Source disclosures use approved content-addressed snapshots, not arbitrary sibling-repository reads at runtime; see [embedded source references](source-references.md). Adding source links does not automatically approve or regenerate their snapshots.

## Security and unresolved evidence

The catalog is public portfolio content. Shared annotations are intended for this local installation; there is no account authentication or private-library authorization. CSRF validation and same-origin checks protect browser mutations without establishing user identity. SVG rejection patterns and source-snapshot screening are defense measures, not general sanitization guarantees.

The current catalog validator checks local links, anchors, language paths, question IDs, retained headings and reachability. It cannot establish translation accuracy, runtime pagination, external URL reachability or deployment readiness. Application test definitions cover catalog synchronization, pagination, path traversal, shared access and language separation and CSRF; reading those tests is not executing them.

Evidence: `backend/app/services/catalog/{files,sync,page,presenter}.rb`, `backend/app/controllers/api/{projects,bookmarks}_controller.rb`, `backend/db/schema.rb`, `backend/test/models/catalog_test.rb`, `backend/test/integration/{catalog_api,bookmarks_api}_test.rb`, `frontend/lib/{catalog,documentation,document-links}.ts` and `compose.yaml`. See [audit scope and remaining work](../operations/documentation-audit-2026-10-19.md).

## Shared annotation migration

On 2026-10-20, the local database retained 60 notes, 60 highlights and 12 bookmarks through the expand/contract migration. Existing IDs, note bodies, ranges and foreign keys are preserved. Conflicting seed keys keep the earliest ID canonical and rename later keys with a deterministic `__legacy_demo__<id>:` prefix. They remain explicitly tagged for cleanup; no distinct notes are merged. The migration is irreversible because removed ownership cannot be reconstructed. Take a restricted database backup before applying it. Notes without highlights remain independently anchored; combined lists use explicit foreign-key relationships instead of guessing by identical text.
