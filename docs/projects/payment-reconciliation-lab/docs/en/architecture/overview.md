# Architecture and domain

[English](overview.md) | [Português](../../pt-BR/architecture/overview.md)

Payment Reconciliation Lab is transitioning from the Aurora Bakery study scope toward payment reconciliation. The infrastructure identity has changed; the current application still exposes a legacy read-only catalog. Reconciliation and Stripe are planned, without implemented reconciliation entities, endpoints, jobs or provider calls. The [restructuring report](../operations/historical-refactor-report.md) preserves the earlier commerce history, not the current product roadmap.

## Implemented modules

A Spring Boot application serves `GET /api/v1/products`. `ProductController` delegates to a transactional read-only `CatalogService`; the service calls a concrete Spring Data JPA `ProductRepository` and maps entities to explicit `ProductSummary` records. This is pragmatic layering, not strict dependency inversion: application imports infrastructure and entities use JPA annotations.

Products retain legacy slug/name/description, BRL price, category, optional image metadata, featured/availability state and timestamps. The query includes AVAILABLE and TEMPORARILY_UNAVAILABLE, ordered by featured descending and name ascending. `purchasable` is true only for AVAILABLE; it is metadata, not a working purchase flow. DISCONTINUED and ARCHIVED rows are retained but hidden. There is no pagination, write endpoint, inventory or upload implementation.

Angular lazily loads `/products`; relative `/api` calls use the development proxy to `backend`. A discriminated signal state distinguishes loading, error, empty and populated results; retry issues a new request. The legacy storefront remains visible, including bakery wording. No reconciliation UI exists yet.

Security permits explicit catalog/health GETs and dev-profile OpenAPI, then denies other routes. CORS lists allowed origins, methods and headers; no login or persisted identity exists. CUSTOMER/ADMIN and purchase-policy code/tests have been removed. Client failures use generic Problem Details; server logs retain exceptions. Stateless/CSRF-disabled configuration describes the current read API and must be revisited before authenticated writes.

## Database evolution

Flyway retains V1 and V2. V2 renames `stores` to `legacy_stores` and creates constrained products; fresh databases apply both migrations. No reconciliation migration exists. Hibernate validates rather than generates schema, and `open-in-view=false` keeps entity mapping within the service transaction. Preserve applied migration checksums and initialized database credentials during the [infrastructure transition](../docker/runtime.md).

Catalog seed SQL is removed. `DevelopmentSeedConfiguration` instead rejects `app.seed.enabled=true` with an ApplicationRunner failure: keep `DEV_SEED_ENABLED=false`. The base runtime still runs Flyway automatically; the development override disables it and therefore requires an initialized schema. No reconciliation fixture generation is implemented.

## Planned lifecycle and boundaries

Only the direction toward reconciliation and a Stripe test integration is established. The reserved `STRIPE_SECRET_KEY` has no application binding, validation or SDK consumer; Compose does not pass it to the backend. A public example entry is not an implemented integration.

Before adding workflows, define reconciliation inputs, matching rules, monetary/currency representation, discrepancy states, replay/idempotency and authorized review operations. Signed provider events, server-owned financial records and duplicate-event handling are reasonable study considerations, not selected or implemented contracts. Earlier CUSTOMER/ADMIN registration, loyalty, bakery checkout, order states and uploads belong to the historical commerce scope and are not current delivery commitments. See the [roadmap](roadmap.md) and [architecture decisions](../adr/architecture-decisions.md).

## Implemented request sequence

```mermaid
sequenceDiagram
    participant UI as Angular
    participant API as ProductController
    participant S as CatalogService
    participant DB as PostgreSQL via JPA
    UI->>API: GET /api/v1/products (development proxy)
    API->>S: list()
    S->>DB: visible availability, featured/name ordering
    DB-->>S: products
    S-->>API: ProductSummary DTOs inside transaction
    API-->>UI: JSON array or generic Problem Details
```
