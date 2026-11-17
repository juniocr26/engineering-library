# Current catalog, domain transition and interview study

Static review: 2026-10-18 at `71b8b8f22d38f08e8ab40cb519f8b1a0985b74c6`. The repository name and roadmap target payment reconciliation, but the inspected application delivers a read-only single-bakery catalog. Java/Spring Boot, PostgreSQL/Flyway and Angular implement that catalog; Stripe, webhooks, settlement matching and payment persistence are not implemented. This project is independent of the other portfolio applications.

## Run and follow a request

Follow [setup](setup.md) from a fresh clone: copy `.env.example` without overwriting existing configuration, configure a private local database password and use the main Compose workflow. UI: localhost:4200/products; API: localhost:8080/api/v1/products. Startup applies Flyway and validates JPA mappings. Existing installations must follow the [data-preserving transition](../docker/runtime.md); keep `DEV_SEED_ENABLED=false`. These commands were not executed in this maintenance task.

Angular `ProductApi.list()` calls same-origin GET `/api/v1/products` through its proxy. Spring allowlists that GET; `ProductController` calls `CatalogService`, whose read-only transaction queries the JPA repository and maps to `ProductSummary`. DTO serialization is separate from exposing JPA entities. With open-in-view disabled, mapping occurs within the service boundary. The UI distinguishes loading, error, empty and populated states; retry repeats a read.

V1 is immutable migration history. V2 renames the former table to `legacy_stores`, preserves its rows and creates `products` with UUID identity, unique constrained slug, positive NUMERIC(12,2) price, allowed availability states and timestamps. There is no tenant/store foreign key in the new catalog. Availability filtering and `purchasable` response policy must be distinguished from persisted SQL constraints. Preserving historical rows is not proof of backup/restore readiness.

## Security, failure and alternatives

Spring Security is stateless, permits only selected GET routes and denies the rest. Swagger is dev-only. There is no account login/JWT or payment authorization protocol. CORS allows configured origins with GET and no credentials; it is browser policy, not client identity. CSRF disabling must be reevaluated if cookie-based mutation is introduced. Generic Problem Details responses avoid exposing server diagnostics.

The catalog has no pagination or measured query capacity. Read-only transaction semantics do not imply distributed consistency or a future provider transaction. PostgreSQL constraints protect local rows; a future payment provider would need signature verification, replay handling, durable event identity and reconciliation rules. A possible provider adapter or outbox is a proposal, not an integration proven by this code.

## Interview rehearsal

**Introductory — What can you demonstrate today?** A catalog read through Angular, HTTP, Spring service/DTO, JPA and PostgreSQL, with explicit security allowlisting and migration history. Follow-up: describe planned reconciliation separately; do not claim Stripe calls, payment encryption or financial outcomes.

**Intermediate — Why DTOs inside a read-only transaction?** They make the response explicit and avoid relying on a live persistence context during serialization. Follow-up: a simple projection could reduce mapping overhead; measure the query before claiming that benefit here. A read-only annotation is not authorization or proof of zero side effects throughout startup.

**Challenging — How would you evolve the database safely?** Keep applied V1/V2 immutable, add a forward migration and preserve required historical data. Follow-up: rolling back code does not reverse data migrations; test restore into a disposable database and define compatibility before changing persistent identity. Those exercises were not performed now.

[Tests](../testing/strategy.md) separate API/security and seed-policy tests from `ProductPostgresIT` real PostgreSQL behavior; frontend tests exercise rendering states. H2/unit evidence does not establish Flyway/PostgreSQL compatibility or a production rollout. Inspect the [API](../api/catalog-contract.md), [database](../database/catalog-and-transition.md) and [decisions](../adr/architecture-decisions.md). Remaining gaps include every payment workflow, real provider contracts, production identity/TLS, pagination/query plans and verified backup restoration. No application tests were run here.
