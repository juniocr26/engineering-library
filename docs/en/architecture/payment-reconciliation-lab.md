# payment-reconciliation-lab: implementation dossier

[English](payment-reconciliation-lab.md) | [Português brasileiro](../../pt-BR/architecture/payment-reconciliation-lab.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

## Implemented catalog API and UI

The project name expresses a reconciliation direction; the current business interface is the retained read-only catalog. Angular lazy-loads `/products` and calls relative `GET /api/v1/products`. The development proxy forwards to Spring Boot. `ProductController` delegates to `CatalogService.list`, which uses a read-only transaction and a Spring Data JPA repository, then maps entities to `ProductSummary` records before returning a JSON array. No reconciliation, checkout, order or upload endpoint exists.

The result includes AVAILABLE and TEMPORARILY_UNAVAILABLE, ordered by featured descending and name ascending. DISCONTINUED and ARCHIVED remain stored but hidden. DTO fields include UUID, slug, name, description, BigDecimal price, category, optional imagePath, featured, availability and purchasable. Purchasable is true only for AVAILABLE but does not authorize or execute a purchase. Angular's interface uses a number for price and does not include every server field; its compile-time type does not validate arbitrary HTTP JSON. Loading/error/empty/ready states and manual retry make request outcomes visible.

No pagination, cache or total-count contract exists. The repository materializes all matching entities, then DTOs, and the frontend receives the complete list. This is simple for a small retained catalog but has memory/network/query costs as data grows. Pagination would need stable tie-breaking, cursor/page semantics and UI state; it is hypothetical. Unexpected exceptions return generic 500 Problem Details; logs retain the exception. Do not expose logs or infer a payment failure taxonomy from a generic catalog error.

## Catalog schema and domain transition

Flyway V1 creates stores. V2 renames it to `legacy_stores`, preserving rows, and creates `products`. IDs are UUID primary keys; slug is unique with a format CHECK; names/categories must contain non-whitespace content; price is positive NUMERIC(12,2); availability is one of four explicit values; timestamps default to current time. There is no foreign key connecting products to the retained stores and no reconciliation ledger, provider-event or matching table. `updated_at` has a creation default, not a database trigger proving it changes on every update.

JPA uses BigDecimal for price and Hibernate validates schema instead of generating it. `open-in-view=false` means entity mapping must finish inside the service transaction rather than relying on persistence access during serialization. `readOnly=true` is a transaction hint/intent; it is not a replacement for database privileges or authorization. The current service imports the concrete JPA repository, so the layering is useful but not strict dependency inversion.

Unique slug and primary-key indexes serve identity; no catalog filter/sort index is declared by the migrations. Do not claim an optimized query plan without an EXPLAIN and representative data. Monetary scale avoids binary-floating rounding in the persisted catalog, but a real reconciliation domain would also need explicit currency, rounding rules, immutable financial source records, adjustment semantics and matching identities. These are unselected future requirements. Preserve applied migration history/checksums; renaming Compose services or a volume does not transform initialized role/database identity or domain data.

## Read API security and future payment boundaries

Spring Security permits specific product/health GETs and dev-profile OpenAPI, then denies all other routes. There is no persisted login, role model or authenticated administrator. CORS only allows configured origins, GET, Accept/Content-Type and no credentials; non-browser clients do not enforce CORS. Stateless sessions and disabled CSRF match the current read-only surface but do not establish a safe future cookie-authenticated write design. Blocked routes produce generic 403 Problem Details.

The base config hides messages/stack traces/binding errors from server responses. `ApiExceptionHandler` logs unexpected exceptions while returning generic 500. Detailed logs require restricted access/redaction: client sanitization does not sanitize server diagnostics. Environment-based database credentials are configuration, not embedded public documentation; this review did not read real environment files. Local database ports are loopback-bound; that is development isolation, not an audited production perimeter.

Stripe is not implemented: no SDK consumer, binding, webhook verification, provider call or injected Compose Stripe key exists. A reserved template entry does not change that. Future reconciliation would need authorized review operations, provider-event authentication, duplicate/replay policy and audit records. Signed provider payloads, TLS, application identity and idempotency protect different boundaries; none may be claimed from the existing CORS/catalog policy. These are hypothetical requirements, not delivered security controls.

## Startup, deployment and test boundaries

The base runtime applies Flyway and validates the schema. The development override sets `SPRING_FLYWAY_ENABLED=false`, so it requires an already initialized schema; disabling migrations does not create missing tables. `DEV_SEED_ENABLED=true` activates a runner that deliberately fails startup because reconciliation fixtures do not exist. Keep it false; there is no seed job to retry. Compose waits for database health in the base setup, while the development override disables backend health and changes the frontend dependency to service_started.

Spring liveness includes application state; readiness includes state and database connectivity. Neither tests matching, provider credentials or webhook processing. Angular retry repeats a GET rather than retrying a financial operation. MockMvc tests replace the catalog service, Angular tests replace HTTP and opt-in PostgreSQL integration uses Testcontainers for migrations/constraints/visibility. The current source inventory is 7 backend unit/API methods, 5 PostgreSQL methods and 4 Angular cases; this is not coverage percentage or a new passing result. No application tests ran here.

Preserve initialized database credentials and the actual volume during the infrastructure rename. The existing-db override explicitly reuses an external volume rather than creating a silent replacement. Before a real update, review compatibility, take an independently recoverable backup, stage migration verification and define rollback of code plus forward-compatible schema. None of these runtime procedures were executed here. Reverting an image or a Flyway file is not restoring lost data. Evidence gaps include production rollout/TLS, backup restore, large catalog query plans and the entire reconciliation lifecycle. Payment categories must be marked not implemented, rather than filled with fictional webhook contracts or ledger flows.

## Supporting evidence

- [api/catalog-contract](../../../../payment-reconciliation-lab/docs/en/api/catalog-contract.md)
- [database/catalog-and-transition](../../../../payment-reconciliation-lab/docs/en/database/catalog-and-transition.md)
- [security/read-api-boundaries](../../../../payment-reconciliation-lab/docs/en/security/read-api-boundaries.md)
- [operations/deployment-and-evidence](../../../../payment-reconciliation-lab/docs/en/operations/deployment-and-evidence.md)
- [Interview / Entrevista](../interviews/payment-reconciliation-lab.md)

## Source reconciliation — 2026-10-18

`71b8b8f22d38f08e8ab40cb519f8b1a0985b74c6`. The source, API/CLI entry points, persistence/resource boundaries and test definitions were reviewed statically. The existing explanations and interview answers remain applicable within their recorded limits. No runtime test results were produced. See the project’s standalone [implementation and interview path](../../../../payment-reconciliation-lab/docs/en/guides/implementation-study.md).
