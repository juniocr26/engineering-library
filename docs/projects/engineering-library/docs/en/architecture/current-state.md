# Engineering Library: current architecture

> Historical scaffold inspection recorded on 2026-10-18. For the current catalog, internal Markdown reader, search and anonymous bookmarks, see [Book frontend and catalog](../guides/book-frontend.md).

## Purpose and evidence boundary

The library preserves software engineering mechanisms, decisions, limits and interview reasoning in English and Brazilian Portuguese. Local Markdown is the current content source. Static inspection on 2026-10-18 examined routes, application classes, frontend page/status component, Compose, database configuration, dependency declarations, environment-template keys and test definitions. Existing execution reports remain dated evidence; no application was run for this catalog.

## Implemented foundation

`backend/` contains a Rails 8.1.4 API scaffold on Ruby 3.4.11, ActiveRecord with the `pg` adapter, Puma and the conventional controller/model/job base classes. `config/routes.rb` exposes `/up` through Rails health. There is no implemented collection/chapter endpoint, ingestion pipeline or domain model for catalog records. PostgreSQL configuration separates development and test databases using the configured name and `_test` suffix.

`frontend/` is a separate Next.js 16.4.2 App Router application with React 19.3.1 and TypeScript. Its landing page links to repository documentation. Its server component requests Rails `/up` with a three-second timeout and renders an unavailable state on failure. This is a boot/liveness indication, not proof of database readiness or a rendered interactive documentation book.

`compose.yaml` defines PostgreSQL, backend and frontend. Container traffic uses service names and internal ports; published ports bind to loopback. Backend startup depends on healthy PostgreSQL; frontend startup depends on healthy Rails. Development source and dependency directories are bind-mounted, including `backend/vendor/bundle` and frontend `node_modules`. PostgreSQL uses the host `.dockerized-postgres` directory, not a Docker named data volume. Data surviving recreation is persistence, not a verified backup.

## Responsibilities and trade-offs

Rails conventions already supply boot, HTTP, persistence configuration and testing structure. They reduce initial infrastructure work; this is an explanation of fit, not evidence that the author benchmarked frameworks. Next.js separates presentation and server-side fetching from the Rails API, at the cost of another build and deployment boundary. There is no browser-origin API call in this scaffold and therefore no demonstrated need for CORS middleware today.

Clean Architecture is a future boundary principle: use cases should express catalog operations independently of transport, filesystem adapters and inference providers when those use cases exist. Current Rails base classes are not evidence of completed domain/application layers. Introducing abstractions before a concrete contract would add maintenance without a demonstrated benefit.

## Catalog contract

Navigation is Library → Project → Language → Index → Category → Document. `docs/projects/<repository>/` is a collection; its identifier matches the workspace directory. Language paths and ADR filenames remain stable. Category indexes list pages as chapters. English and Portuguese indexes provide project-selection entry points. Topics appear in descriptions and chapter names, with no separate subject hierarchy or search index.

The Engineering Library project entry explains only this project. It references existing canonical environment and validation guides; it does not contain another copy of the portfolio catalog. Project collections retain their own available reference material; removed root-language dossiers are not recreated. Source repository identity, revision, inspected paths and evidence limits accompany each collection. Copies are snapshots and do not inherit runtime verification from a successful link check.

## Security and unresolved evidence

Only public portfolio documentation belongs here. Runtime environment values, keys, database contents and private work documentation are excluded. Existing source links are for traceability, not permission to read restricted paths. No authentication or private-library isolation service exists in the scaffold. Public/private separation for future ingestion requires explicit roots, access control and review before publication.

Source-level anchors for this review: `backend/config/routes.rb`, `backend/config/database.yml`, `backend/app/`, `backend/test/integration/health_test.rb`, `frontend/app/page.tsx`, `frontend/components/backend-status.tsx`, `frontend/package.json`, `backend/Gemfile`, `compose.yaml` and template variable names. Their repository links are in the project README. No performance, production readiness, restore result or hardware minimum was measured in this milestone.
