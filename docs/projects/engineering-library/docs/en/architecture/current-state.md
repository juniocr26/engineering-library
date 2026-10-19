# Engineering Library: current architecture

Static source review: 2026-10-19. This page describes the current working tree; historical scaffold descriptions are superseded. [Book frontend and catalog](../guides/book-frontend.md) describes the reader in greater detail.

## Purpose and evidence boundary

The Library maintains bilingual engineering explanations, project FAQs and source evidence. Markdown in `docs/projects/` owns document bodies and bios. Rails serves catalog metadata and anonymous bookmarks; Next.js renders the internal book reader. Source and test definitions were inspected, without starting services or executing database-backed tests. No production deployment, measured capacity or AI agent is established.

## Implemented foundation

`backend/config/routes.rb` exposes `GET /api/projects`, `GET /api/projects/:id`, the project icon endpoint, bookmark list/create/delete and `/up`. `CatalogProject` and `Bookmark` have real PostgreSQL schema, validations and indexes. `/up` indicates Rails boot health; it does not query the catalog or certify PostgreSQL readiness.

`Catalog::Sync` scans catalog directories, validates localized bio identity/name agreement and duplicate stable IDs before writes. A transaction-scoped advisory lock serializes database updates; records are matched by `stable_id`, renamed by slug and deactivated when absent. Unchanged records avoid writes. Validation failure retains the last valid database index. The transaction does not snapshot files: keep catalog files stable while synchronizing. Markdown document edits do not require database ingestion; metadata edits need explicit `catalog:sync`.

`Catalog::Page` selects active records with fixed page size five and deterministic `lower(display_name) COLLATE "C", stable_id` order. Offset pagination is simple and index-supported but is not a snapshot across requests during catalog changes. Next fetches catalog JSON server-side with `cache: 'no-store'` and a five-second timeout. Its collection filesystem reader is separate from the Rails metadata API.

`compose.yaml` defines PostgreSQL, Rails and Next. Ports bind to loopback. PostgreSQL data uses `.dockerized-postgres` on the host; this is persistence, not a verified backup. Both application services receive the documentation collection read-only. Dependency/build directories remain development bind mounts. Startup health dependencies do not implement automatic application-level recovery after every dependency failure.

## Responsibilities and trade-offs

Rails owns indexed metadata, catalog pagination and bookmark persistence. Next owns Markdown rendering, logical document order and browser-measured physical pagination. Filesystem content and database metadata are different consistency boundaries. `Catalog::Files.read` resolves real paths within a validated project; `collectionFile` applies its own scoped checks on the Next side. Neither check is a race-free adversarial filesystem sandbox.

Anonymous bookmarks identify a browser through a signed, HttpOnly, SameSite=Lax cookie; PostgreSQL stores its SHA-256 digest. Mutations require a verifier token bound to that digest and purpose. This is browser-local identity and CSRF protection, not login or cross-device synchronization. The database unique index prevents duplicate logical locations. The 200-bookmark admission check uses a count before insert, so it is not a transactional concurrency cap. Anchor syntax is validated, but existence of every anchor is not verified on creation.

## Catalog contract

Navigation is Library → Project → Language → Category → Document. `documentationEntries` merges relative IDs across both languages, sorts deterministically, excludes navigation-only indexes and retains substantive ones. Missing translations have no destination. `reading-order.ts` derives neighboring document routes from those same entries. Physical page counts depend on fonts, diagrams, images and viewport measurements; URLs/bookmarks retain logical document/anchor identities instead of physical page numbers.

Technical FAQ answers live directly in `faq/index.md`. Existing `study-guide.md` paths and heading anchors remain compatibility references. Source disclosures use approved content-addressed snapshots, not arbitrary sibling-repository reads at runtime; see [embedded source references](source-references.md). Adding source links does not automatically approve or regenerate their snapshots.

## Security and unresolved evidence

The catalog is public portfolio content. It has no user-account authentication or private-library authorization. Bookmark reader isolation is narrower than access control over documents. Cookie signing depends on a stable secret; losing browser identity prevents ordinary access to previous anonymous bookmarks. SVG rejection patterns and source-snapshot screening are defense measures, not general sanitization guarantees.

The current catalog validator checks local links, anchors, language paths, question IDs, retained headings and reachability. It cannot establish translation accuracy, runtime pagination, external URL reachability or deployment readiness. Application test definitions cover catalog synchronization, pagination, path traversal, anonymous isolation and CSRF; reading those tests is not executing them.

Evidence: `backend/app/services/catalog/{files,sync,page,presenter}.rb`, `backend/app/controllers/api/{projects,bookmarks}_controller.rb`, `backend/db/schema.rb`, `backend/test/models/catalog_test.rb`, `backend/test/integration/{catalog_api,bookmarks_api}_test.rb`, `frontend/lib/{catalog,documentation,document-links}.ts` and `compose.yaml`. See [audit scope and remaining work](../operations/documentation-audit-2026-10-19.md).
