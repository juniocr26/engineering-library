# Architecture Decisions & Trade-offs

[English](architecture-decisions.md) | [Português](../../pt-BR/adr/architecture-decisions.md)

This document explains the current retained catalog and the transition toward payment reconciliation. Implementation statements come from source, migrations, configuration and tests. Unless an existing document records intent, the rationale below evaluates the current architecture rather than claiming to recover its original motivation. Alternatives are review options, not evidence of a historical evaluation.

## Implementation status

- **Implemented:** Spring Boot catalog, PostgreSQL schema, Angular storefront, deny-by-default HTTP security, Docker development environment and catalog/security and retired-seed rejection tests.
- **Retired:** CUSTOMER/ADMIN vocabulary, purchase policy and catalog seed. Historical commerce decisions remain in the restructuring report.
- **Planned / future work:** reconciliation workflows and Stripe test integration; domain rules and access contracts still need definition. See the [roadmap](../architecture/roadmap.md).

## Decision: Retain a modular monolith during the domain transition

**Context.** The implementation retains a bakery catalog during transition; no reconciliation workflow exists yet.

**Decision and why.** One Spring Boot application retains catalog and configuration packages. The products schema has no tenant ownership. This keeps current catalog queries within one application/database boundary; microservices would add network failures and deployment coordination before there are independent workflows to deploy.

**Alternatives.** A multi-tenant SaaS would require tenant-aware keys, authorization and isolation tests. Independently deployed catalog/order services would require contracts and consistency across services.

**Trade-offs and consequences.** Deployment and debugging are simpler, but package boundaries are conventions rather than isolated services. Catalog separates controller, application service, domain entity and JPA repository; the service directly imports the infrastructure repository, so this is not strict dependency inversion. Payroll, ERP and accounting remain out of scope. No broker or background processing is implemented.

**Revisit when.** Independently owned modules need different deployment schedules or measured workloads require independent scaling. A multi-store product would require an explicit scope change and data-isolation design.

**Evidence:** [CatalogService](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java), [V2 schema](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/db/migration/V2__single_bakery_catalog.sql), [domain overview](../architecture/overview.md).

## Decision: Java and Spring Boot for typed application boundaries

**Context.** Catalog data and future monetary rules need explicit contracts and testable server-side behavior.

**Decision and why.** Java records express response DTOs, enums constrain availability, and `BigDecimal` represents decimal catalog prices. Spring MVC, dependency injection, Security, JPA, Flyway and Actuator integrate HTTP, persistence and operations in one runtime. The present benefit is visible in a thin controller and transactional read service; it is not a claim of measured performance or an original language-selection motive.

**Alternatives.** A smaller Python/FastAPI or Go HTTP application could serve this catalog but would require different persistence/security integration. Spring JDBC could make SQL more explicit than JPA.

**Trade-offs and consequences.** Framework configuration and a Java 25 toolchain are required even for a small read API. ORM annotations couple the product entity to persistence; logical boundaries are clear but not framework independent. Explicit DTO mapping avoids exposing entity internals and allows the public contract to evolve separately.

**Revisit when.** Framework cost materially impedes deployment, or query complexity warrants explicit SQL. First measure the actual workload.

**Evidence:** [pom.xml](../../../../../../../payment-reconciliation-lab/backend/pom.xml), [ProductSummary](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/ProductSummary.java).

## Decision: PostgreSQL with versioned schema ownership

**Context.** The implemented catalog needs unique slugs, valid lifecycle states and positive decimal prices. Future orders/customers are relational, but those tables do not exist today.

**Decision and why.** PostgreSQL enforces checks and uniqueness; Flyway owns schema evolution and Hibernate validates rather than generates tables. `open-in-view=false` and mapping inside a read-only transaction keep persistence work out of HTTP serialization.

**Alternatives.** An embedded database would reduce local infrastructure but would not exercise PostgreSQL-specific constraints. Document storage would move more consistency checks into application code. Automatic ORM schema updates would obscure migration history.

**Trade-offs and consequences.** Database changes need explicit migrations. V1 remains immutable; V2 renames `stores` to unexposed `legacy_stores` instead of deleting old rows. Fresh databases also retain that unused table. The catalog loads all visible products into a list; there is no pagination or cache, so response size and database work grow with the catalog.

**Revisit when.** Catalog size warrants pagination/index analysis, or a reviewed retention policy permits removing legacy data. Orders will need transaction and snapshot rules before implementation.

**Evidence:** [migrations](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/db/migration), [application.yml](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/application.yml), [PostgreSQL integration tests](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java).

## Decision: Availability and historical lifecycle instead of inventory

**Context.** Existing domain documentation models made-to-order bakery products rather than ingredient or warehouse accounting.

**Decision and why.** AVAILABLE and TEMPORARILY_UNAVAILABLE remain public; only AVAILABLE is marked purchasable. DISCONTINUED and ARCHIVED are excluded from the public query. Availability answers whether a product can be offered without pretending to measure physical stock. Featured ordering is independent of discounts.

**Alternatives.** Quantity reservations would support finite stock but require concurrency, release/expiry and overselling rules. Physical deletion would simplify storage but lose records useful to future historical references.

**Trade-offs and consequences.** Temporary unavailability remains understandable to customers rather than appearing as a missing product. Rows are preserved, but no mutation API, automatic archive scheduler or order references exist yet. `purchasable` is catalog information, not checkout enforcement. The UI does not offer purchases.

**Revisit when.** Finite batches require stock reservations, or administrative lifecycle/retention requirements become concrete.

**Evidence:** [Product](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/domain/Product.java), [CatalogService](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java), [ProductPostgresIT](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java).

## Decision: One Angular storefront with explicit request states

**Context.** A customer must distinguish a slow request, an empty catalog and a backend failure.

**Decision and why.** One Angular app lazily loads the catalog; `ProductApi` owns HTTP access and a discriminated signal state drives loading/error/ready rendering. BRL formatting, status/alert roles, a skip link and a retry button turn API state into useful feedback. Relative `/api` calls use the development proxy, avoiding Docker hostnames in browser code.

**Alternatives.** Server-rendered HTML would reduce client tooling for a read-only catalog. A separate admin frontend would permit independent releases but duplicate tooling and shared contracts.

**Trade-offs and consequences.** Angular supplies typed components and testing support at the cost of a build/runtime toolchain. Retry issues a fresh HTTP request; no offline cache or automatic retry exists. The API returns image metadata, but the current frontend does not render product images. There are no admin routes, guards or reconciliation screens today. Earlier storefront/admin plans are historical.

**Revisit when.** Search indexing/server rendering becomes a requirement, or administration needs an independent release/security boundary.

**Evidence:** [catalog UI and tests](../../../../../../../payment-reconciliation-lab/frontend/src/app/catalog), [bootstrap/routes](../../../../../../../payment-reconciliation-lab/frontend/src/main.ts), [proxy](../../../../../../../payment-reconciliation-lab/frontend/proxy.conf.cjs).

## Decision: Deny writes until identity is implemented

**Context.** The current application has no identity implementation; its former role vocabulary is removed.

**Decision and why.** Security allows public catalog GETs, non-sensitive health and dev-only OpenAPI, then denies all remaining routes. Explicit CORS origins and generic Problem Details limit accidental exposure. This provides a safe read-only boundary while identity is unfinished.

**Alternatives.** Temporary public writes would expose privileged operations. An identity provider could provide federation but would add infrastructure before the current login workflow exists.

**Trade-offs and consequences.** No customer login or actual administrator access is possible. Stateless configuration and disabled CSRF describe the current read API, not a settled future authentication strategy. Cookie-based authentication would require revisiting CSRF; bearer authentication would require token validation and lifecycle rules. Exception details are hidden from clients but logged on the server.

**Future review.** Define identity and authorization for reconciliation operations before enabling writes. The former CUSTOMER/ADMIN provisioning direction is historical, not a selected current contract.

**Revisit when.** Any authenticated or mutation endpoint is introduced; select session/token handling before extending the allowlist.

**Evidence:** [SecurityConfiguration](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java), [API/security tests](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductApiTest.java), [identity roadmap](../architecture/roadmap.md).

## Historical decision: Purchase policy retired

The earlier purchase-discount/loyalty policy and its tests were removed on 2026-10-09. They are not prepared current functionality. Their former scope is retained in the [historical report](../operations/historical-refactor-report.md). Reconciliation needs its own monetary/currency and matching rules; a catalog `BigDecimal` field alone does not implement financial reconciliation.

## Decision: Keep reconciliation and Stripe planned until contracts exist

**Context and current boundary.** The catalog persists image-path metadata, but there is no upload or checkout. The application has no reconciliation schema, provider adapter, webhook or Stripe SDK. `STRIPE_SECRET_KEY` is a reserved example setting without binding or backend Compose injection.

**Alternatives for study.** A direct provider integration could accept events, but matching/idempotency and authoritative records would still need definition. An adapter boundary could isolate provider details; it has not been implemented or selected as a finished contract. A durable outbox may be appropriate if future reliable delivery requires it.

**Trade-offs and consequences.** Deferring integration avoids a misleading fake payment/reconciliation flow, while leaving the new product unfinished. Define inputs, money/currency, authorization, signed events and replay semantics before claiming functionality. Historical commerce uploads and loyalty plans are not commitments for this scope.

**Evidence:** [current scope](../architecture/overview.md), [roadmap](../architecture/roadmap.md), [manifest](../../../../../../../payment-reconciliation-lab/backend/pom.xml), [Compose](../../../../../../../payment-reconciliation-lab/docker-compose.yml).

## Decision: Docker for local reproducibility and layered verification

**Context.** Java, Node and PostgreSQL versions must be reproducible without relying on host toolchains.

**Decision and why.** Compose separates db/backend/frontend on one bridge network, binds host ports to loopback, persists PostgreSQL in a named volume and gates startup on health. Pinned image digests and the npm lockfile reduce dependency drift. The backend runtime and frontend use non-root users. The frontend is a development server, not production hosting.

**Alternatives.** Host-only setup removes containers but requires matching toolchains; production orchestration/reverse proxies introduce concerns this local environment does not solve.

**Trade-offs and consequences.** Database startup automatically runs migrations; the retired seed flag causes startup failure if enabled. Launching against existing data can still write migration metadata/schema; the development override disables Flyway for initialized databases. Health/readiness includes database connectivity but is not full production observability. Persistent volumes survive ordinary shutdown.

**Testing choice.** MockMvc with a mocked service checks HTTP/security contracts; seed-guard tests check rejection of the retired flag; opt-in Testcontainers PostgreSQL tests exercise actual migrations, constraints, query behavior and hidden-row preservation. Angular HTTP fakes check request/UI states. Fakes do not prove database behavior; real database tests cost Docker startup and resources. No checkout/payment tests are claimed.

**Revisit when.** Production hosting, deployment automation or failure recovery is required. Keep test database configuration isolated from development data.

**Evidence:** [Compose](../../../../../../../payment-reconciliation-lab/docker-compose.yml), [Docker details](../docker/runtime.md), [tests](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery), [frontend tests](../../../../../../../payment-reconciliation-lab/frontend/src/app/catalog/product-list.spec.ts).
