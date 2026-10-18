# Refactor verification — 2026-10-05

[English](verification.md) | [Português](../../pt-BR/testing/verification.md)

This records the earlier refactor verification, not a new full-stack run during the documentation review. The verification used Docker Desktop with Compose v2 on macOS ARM64. Host Java 17 and missing host Node were bypassed using the repository Java 25 and Node 22 Docker images. Exact pinned dependencies were retained.

| Check | Result |
| --- | --- |
| `docker compose config --quiet` | PASS |
| Fresh `docker compose build` | PASS, both application images |
| `docker compose up --build -d --wait --wait-timeout 180` | PASS, db/backend/frontend healthy |
| Fresh named volume and default network | Created as `aurora-bakery_db_data` and `aurora-bakery_default` |
| Flyway and Hibernate startup | PASS, V1/V2 applied and schema validated |
| Database query | PASS, both migration versions successful, two available and one temporarily unavailable demo products |
| Readiness with database | PASS, UP |
| Frontend `/products` | HTTP 200 |
| Angular proxy `/api/v1/products` | PASS, identical to direct backend response with three demo products |
| Angular production build | PASS, lazy catalog bundle |
| Angular tests | PASS, 4 tests |
| Backend unit and integration tests | PASS, 9 unit/API tests and 6 real PostgreSQL integration tests, zero failures or skips |
| Container startup/runtime logs | No application startup errors; normal PostgreSQL initialization restart and development server/toolchain warnings |

No full browser rendering, authenticated checkout, payment, ADMIN provisioning or production deployment verification is claimed. Those workflows do not exist yet. No admin bootstrap is required for the current public read-only catalog. Required services have no previous project name; immutable V1 migration retains historical directory terminology only.

## Commands executed

```sh
docker compose config --quiet
docker compose build
docker compose up --build -d --wait --wait-timeout 180
docker compose ps
docker compose logs --tail=60
docker build --target build -t aurora-bakery-backend-tests ./backend
docker compose run --rm --no-deps frontend npm test
docker compose run --rm --no-deps frontend npm run build
```

Backend tests ran with the Docker socket and `TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal`, executing `./mvnw -B -ntp verify -Pintegration` in the build-stage image. A read-only source mount included the final test changes during verification. The README documents a rebuilt test image command for fresh clones. Database and HTTP smoke checks used `docker compose exec -T db` (psql) and `docker compose exec -T frontend` (Node fetch), checking migrated rows, API/proxy equality and readiness.

## Architecture documentation review — 2026-10-05

This separate review ran the current backend unit/API source in the existing Java 25 build-stage test image, with a read-only source mount: `docker run --rm -v "$PWD/backend/src:/workspace/src:ro" aurora-bakery-backend-tests ./mvnw -B -ntp verify`. All 9 unit/API tests passed. The initial network-disabled attempt failed because the Maven Wrapper distribution was not available in the image; rerunning with downloads enabled passed. No integration profile, frontend suite, browser checks or application Compose stack was run in this review. The disposable container was removed, and no application database/volume or real environment file was mounted. Earlier full-stack results above are historical.

## Documentation validation — 2026-10-06

No containers were running before this project. `docker compose -f docker-compose.yml -f compose.development.yaml config --quiet` passed. The same files with `up -d` started db/backend/frontend, with Flyway and seed disabled and Hibernate set to validate. Readiness, direct product API, frontend `/products` and proxied API returned HTTP 200 after readiness (an early probe failed while backend was starting). `exec -T frontend npm test` passed 4 tests. Backend `exec -T backend sh ./mvnw -B -ntp test` initially failed 1 of 9 because it inherited `APP_ENV=dev`; `exec -T -e APP_ENV=default backend sh ./mvnw -B -ntp test` passed all 9. No application code was changed. Integration tests and production build were not rerun. No database-writing checks were executed. `stop frontend backend db` stopped all services started here, preserving containers and volumes. Language pairs and local Markdown links/anchors were checked.


## Infrastructure identity transition — 2026-10-09

- Retain: pinned toolchains, PostgreSQL/Flyway history, service names/networking, ports/origins/UIDs and inherited runtime readiness healthcheck. Read-only catalog remains temporarily; reconciliation is not implemented.
- Adapt: Compose identity, images/labels, Maven cache, Spring name, Angular project/package/page title, local `.env`, tracked example and bilingual setup. External-volume override enforces reuse of the inspected initialized volume.
- Retire: isolated purchase policy, unused commerce role, discount binding/validation/tests, catalog seed runner and SQL. Two focused tests prove seeding is disabled by default and that enabling the legacy flag refuses startup.
- Defer: reconciliation schema/fixtures and Stripe SDK/configuration. Empty STRIPE_SECRET_KEY is reserved and currently unused. Java package/Maven group remain `com.aurorabakery`; unchanged applied migrations and historical reports intentionally retain prior terminology. No tracked CI workflow, Makefile or extra environment example was found; modernization hook scripts do not override Compose naming.

Passed: quiet Compose resolution for base, external-volume and development overrides; fresh example defaults agree with backend/Compose; local secret file is ignored/untracked; no retained discount variable/binding; `git diff --check`. Both runtime images built successfully. Java 25 container `mvnw verify` passed 7 unit/API tests in a temporary source copy; Angular passed 4 tests and production build on the final image. Initial offline Maven verification failed due to an incomplete host cache; online retry passed. The initial build was interrupted after go-offline completed and then successfully resumed from cache.

Runtime: stopped old frontend/backend, created a mode-600 logical backup at `/tmp/payment-reconciliation-lab-backups/before-transition.dump`, verified its archive listing, and stopped the old DB before new startup. `up --wait` passed for all three new services. Mount inspection confirms reuse of `aurora-bakery_db_data`. Ordered row fingerprints for every product and Flyway history row matched before/after; three product records and two migrations remain. Internal backend readiness, Angular HTTP/title and frontend API proxy all returned 200. Old application containers remain stopped; no volume deletion/pruning occurred. New services were running at the end of that earlier transition; their current state was not inspected during this documentation-only audit. Backup is temporary local storage, not a durable backup service; retain it elsewhere privately if needed.

Pending: Testcontainers integration suite was not executed. Automatic approval review rejected mounting the Docker socket into the test container because it grants broad daemon control. Unit tests ran without that mount. After explicit approval, rerun the documented integration command in [testing](strategy.md) against disposable Testcontainers databases, never the application DB. Development override was resolved but not started; rollback and backup restoration were documented but not executed. No Stripe or reconciliation runtime checks are claimed. npm installation reported 5 dependency vulnerabilities (3 high, 2 critical); dependency versions were unchanged by this naming transition.

## Static documentation audit — 2026-10-09

Aligned current architecture, decisions, roadmap and setup with the retained read-only catalog, removed pricing/identity vocabulary and rejected seed flag. Source inventory is 7 unit/API methods, 5 opt-in PostgreSQL methods and 4 Angular cases; inventory is not a new passing result. Reconciliation/Stripe remain planned and the reserved key is not bound or injected by Compose. No Docker, builds, tests, database/volume inspection, migrations or transition/backup commands were executed. Earlier service-state statements describe the prior transition, not current Docker state.

The earlier shared interview review is not included in the current catalog; its static link, language and SHA-256 checks remain historical reports, not reproduced evidence here. Runtime environment files and secret-bearing backups were not read or modified.
