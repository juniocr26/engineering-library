# Aurora Bakery restructuring report

> Historical commerce scope. Payment Reconciliation Lab retires the purchase policy and catalog seed. Reconciliation and Stripe remain planned; current infrastructure and transition instructions are in [Docker](../docker/runtime.md).


[English](historical-refactor-report.md) | [Português](../../pt-BR/operations/historical-refactor-report.md)

This report describes the earlier restructuring; its runtime results are historical, not new runs during the documentation review.

## Changes delivered

- Replaced the multiple-store directory module, API and Angular page with a single-bakery product catalog. Renamed the small Java namespace to `com.aurorabakery`, application class/name and Angular/package identities.
- Added explicit availability, featured ordering, BRL prices, descriptions, categories, optional image path metadata and timestamps. Temporary unavailability remains visible; discontinued/archived products remain stored and are hidden publicly.
- Preserved useful security deny-by-default behavior, CORS, sanitized errors, Spring layering, DTOs, Flyway, database readiness, Angular loading/empty/error/retry behavior and pinned build tools/images.
- Added a configurable server-side purchase policy with default ADMIN discount of 15%, non-stacking customer benefits and ADMIN loyalty/marketing exclusion. This is domain preparation, not a checkout implementation.
- Rewrote English scope, domain, setup, payment/authentication direction, architecture decisions and verification documentation. Superseded old network ADRs. English and Brazilian Portuguese guides are maintained in parallel; the Portuguese README links to the Portuguese guides.

## Removed scope

Multiple-store entities, repositories, services, controller, fixture data and `/stores` frontend route; fictional franchise/network copy; store-specific inventory/authorization roadmap; speculative broker/cache infrastructure suggestions. No brokers, SSO provider, payroll, accounting, ERP or additional apps were present to uninstall.

## Database and authentication

V1 is unchanged. V2 renames `stores` to `legacy_stores` without discarding existing rows and creates constrained `products`. No legacy store ownership exists in new product entities. The historical table is deliberately unexposed; eventual removal requires a separate retention decision. Flyway applies schema changes, Hibernate validates, and development-only idempotent fixture SQL inserts three fictional products outside migrations. A fresh Docker named volume was initialized.

No account/authentication implementation existed in the baseline. Public mutations and unmatched routes remain blocked. CUSTOMER/ADMIN vocabulary and purchase policy are prepared, but persisted identity, password hashing, registration, login, internal ADMIN provisioning and role-protected administrative writes remain unfinished. No public ADMIN registration or administrator seed was introduced. The internal password-hashing provisioning command is the documented strategy to implement alongside identity; there is no committed admin secret.

## Frontend and payments

One Angular app retains the storefront, with a lazy `/products` route, prices and unavailability messaging. No admin app was added. Product management, image uploads, customer account pages, cart and checkout remain unfinished. Stripe was absent and remains unimplemented: no real-money processing, fake success endpoint, secret or SDK was added. Documentation describes a test-only payment port and signed authoritative webhooks as a future increment.

## Tests

19 tests passed: 9 backend unit/API tests, 6 real PostgreSQL integration tests and 4 Angular tests. They cover catalog DTOs, empty/error responses, CORS and blocked routes, migration success, constraints, availability visibility/purchasability, preservation of hidden product records, repeatable fixtures, operational/local docs endpoints, ADMIN policy, non-stacking benefits, consent, configurable discounts, rounding and frontend states. Angular production build passed. There are no implemented authentication, loyalty progression or Stripe flows to test yet.

## Docker deliverable

Modified `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.env.example`, ignored local `.env`, backend application configuration and README/Docker documentation. Both `.dockerignore` files were reviewed and retained: they already exclude secrets/build output. No Compose overrides, reverse proxy, Makefile, tracked CI workflow or Docker scripts existed.

Services retained: `db` (renamed from `postgres`), `backend`, `frontend`. No whole service was removed; each existing service supports the simplified architecture. Removed the old `commerce`, `web` and `db_access` network configuration, unused `postgres_data` declaration and legacy bind-mount selector. There are no explicit container names.

Compose project `aurora-bakery` generates containers `aurora-bakery-db-1`, `aurora-bakery-backend-1`, `aurora-bakery-frontend-1`, network `aurora-bakery_default`, volume `aurora-bakery_db_data`, application images `aurora-bakery-backend` and `aurora-bakery-frontend`. PostgreSQL retains the official pinned image. Internal hostnames are `db`, `backend`, `frontend`.

Commands used:

```sh
docker compose config --quiet
docker compose build
docker compose up --build -d --wait --wait-timeout 180
docker compose ps
docker compose logs --tail=60
docker build --target build -t aurora-bakery-backend-tests ./backend
docker compose run --rm --no-deps frontend npm run build
docker compose run --rm --no-deps frontend npm test
```

Backend verification executed `./mvnw -B -ntp verify -Pintegration` inside the build-stage image with a Docker socket, host override and read-only final source mount. SQL and Node fetch checks verified successful migrations, fixture rows, database readiness, frontend startup and direct/proxied API equality. See [verification](../testing/verification.md) and [testing](../testing/strategy.md) for reproducible test commands.

**Historical refactor verification:** the complete development stack started successfully during that verification. This is not a statement of current container state. All three services passed health checks. Logs show no application startup/runtime errors. Standard toolchain/Angular development warnings and PostgreSQL's normal initialization restart remain. No required service/configuration references the old project identity. V1 and its historical schema terminology are retained for migration integrity. Ignored historical modernization logs/generated artifacts are not active configuration.

## Remaining debt and specification limitations

This was a read-only directory foundation, not an existing e-commerce application. The restructuring is implemented, but the full product specification is not complete. Account persistence, secure authentication, CPF validation, optional contact/profile/preferences, controlled ADMIN provisioning, admin product/image/promotion/order operations, storage abstraction, cart, order lifecycle/snapshots, persistent promotion/loyalty configuration, paid-order progression, Stripe integration/webhook verification, notifications and account/admin UI require new implementation. The pricing policy alone does not enforce behavior in purchases that do not yet exist. No claims are made for these absent workflows.

The current product constructor supplies basic catalog defaults; future admin creation needs explicit validated inputs and controlled lifecycle/timestamp updates. Currency is currently BRL by project convention. The unused historical table remains. No browser visual QA, production Angular server, production deployment, persistent image volume or upload security verification is claimed. Current stateless CSRF-disabled security must be reconsidered with the authentication choice before writes are enabled.

Intentionally deferred: SSO, WhatsApp, object storage, automatic configurable archiving and durable background delivery. These require no additional infrastructure today. Multi-tenancy, payroll, ERP and accounting are outside scope.

**Recommended next increment:** implement and test shared persisted identity with CUSTOMER-only registration, hashed passwords, an explicit internal ADMIN provisioning command and backend role authorization; then enable administrative product mutations in the same Angular application.

## Current boundary — 2026-10-09

The counts, commerce policies, fixture insertion and recommended next increment above describe the earlier refactor. Current source has removed identity/pricing packages, purchase-policy tests and seed SQL; enabling the retired seed flag fails startup. Reconciliation/Stripe remain planned. Use [current architecture](../architecture/overview.md), [roadmap](../architecture/roadmap.md) and [test inventory](../testing/strategy.md) for today’s state. No historical runtime results were rerun in this documentation audit.
