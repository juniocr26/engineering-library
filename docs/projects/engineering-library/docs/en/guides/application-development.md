# Application development

Current review: 2026-10-19. Rails serves the PostgreSQL-backed catalog and anonymous bookmarks; Next renders the bilingual internal book. The setup below retains its development scope; see [current architecture](../architecture/current-state.md) and [reader guide](book-frontend.md) for present responsibilities.

## Versions and architecture

Ruby 3.4.11, Rails 8.1.4, PostgreSQL 18 (official `18-bookworm` major-pinned image), Node 24.22.0, Next.js 16.4.2, React 19.3.1, TypeScript 5.9.3, ESLint 9.39.5. Gemfile.lock and package-lock.json pin dependencies. PostgreSQL minor image updates are intentional; this development environment is not a production deployment.

Browser :3099 → Next.js :3000 → Rails :3000 on Compose → PostgreSQL :5432. Rails is also exposed on loopback :3098. Next catalog requests use server-side `BACKEND_URL`, `cache: no-store` and a five-second timeout. Rails `/up` remains boot liveness, not a catalog/database query. Current services/models implement catalog sync, pagination and anonymous bookmarks; the reader also implements page-turn transitions. There is no account authentication, AI inference or automatic documentation-generation pipeline. Browser API access uses same-origin Next routes; the reviewed Rails CORS initializer is inactive.

```text
backend/                  Rails API, config, db, test, Dockerfile, Gemfile.lock
  vendor/bundle/          ignored, Linux gems physically on host
frontend/                 App Router, components, public, Dockerfile, package-lock.json
  node_modules/           ignored, Linux packages physically on host
docs/projects/engineering-library/docs/en/guides/      application documentation; existing guides retained
docs/projects/engineering-library/docs/pt-BR/guides/   equivalent Portuguese documentation
tools/                    existing documentation validators
.dockerized-postgres/     ignored, PostgreSQL 18 cluster under 18/docker
.env                      ignored, local credentials
.env.example              configuration template
compose.yaml              three services, no named dependency/data volumes
```

## Setup and lifecycle

Install Docker Desktop on macOS or Docker Engine with the Compose plugin on Linux using the [official installation guide](https://docs.docker.com/engine/install/). Enable the engine, allow project file sharing, and ensure ports 3099, 3098 and 5499 are free. No host Ruby or Node installation is needed.

The initial implementation generated `.env` locally with an ASCII alphanumeric 12-character database password containing upper/lowercase letters and digits, and a random Rails secret. Neither is committed. On a fresh clone run `python3 tools/init_dev_env.py` (Python 3.10+); it creates `.env` without replacing an existing file. The example lists all variables. On Linux set LOCAL_UID and LOCAL_GID to `id -u` and `id -g` before installing dependencies. macOS Docker Desktop supports the default 1000 IDs. Keep the bind-mounted source and dependency folders writable by these IDs. If previously created files belong to another ID, adjust ownership deliberately; do not recursively change PostgreSQL ownership to your app user. The official postgres entrypoint manages its own data ownership.

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# In a second terminal, first setup only (and after adding migrations):
docker compose exec backend bin/rails db:prepare catalog:sync
# Open http://localhost:3099 and http://localhost:3098/up
# Stop, preserving all bind-mounted data:
docker compose down
```

PostgreSQL creates the development database on first cluster initialization. `db:prepare` explicitly initializes Rails schema and pending migrations; startup does not run migrations. The API waits for healthy PostgreSQL; the frontend waits for healthy Rails. A dependency failure prevents a ready state. Source bind mounts support Rails reload and Next webpack development reload (chosen for predictable Docker file watching). A new frontend process runs `npm ci` to synchronize the exact lockfile; backend checks installed gems and installs missing ones. Dependencies installed into image layers validate builds but are hidden by source mounts at runtime; startup restores them physically on the host. These are development images, not minimal production images.

## Dependencies and commands

```sh
docker compose exec backend bundle install
docker compose exec frontend npm ci
# If the services cannot start:
docker compose run --rm --no-deps backend bundle install
docker compose run --rm --no-deps frontend npm ci
# After changing Gemfile/package.json, update the corresponding lockfile:
docker compose exec frontend npm install
docker compose restart frontend
docker compose exec backend bin/rails db:migrate
docker compose exec backend bin/rails console
docker compose logs -f backend frontend postgres
```

Gems and Node native packages compiled for Linux/CPU architecture cannot be reused by native macOS tools or a different CPU architecture. Run development commands in containers. Reinstall dependencies when changing container runtime platform. `npm ci` intentionally reconstructs node_modules; stop the frontend before external recovery if files are in use. Commit lockfile changes, never dependency contents. Never run concurrent installs into the same directory.

## DBeaver and persistence

Connect with PostgreSQL driver, host `localhost` (or `127.0.0.1`), port `5499` or POSTGRES_PORT, database `engineering_library`, username `admin`, and password read privately from local `.env`. Local SSL is not configured: disable SSL for this local connection. The port binds only to 127.0.0.1. Rails always uses `postgres:5432`; changing the published port does not change internal networking.

If connection fails, inspect `docker compose ps` and `docker compose logs postgres`. Check the engine is running, the port is free and DBeaver uses the configured published port. Change POSTGRES_PORT in `.env` and recreate with `docker compose up -d postgres` if the configured host port is occupied. An authentication failure after editing `.env` may mean the existing role still has the old password: initialization variables only affect a new cluster. Coordinate an authenticated `psql` session and interactive `\password admin`, then update `.env` and recreate the backend. Never delete data to solve authentication errors.

Data survives container recreation under `.dockerized-postgres/18/docker`. Deleting `.dockerized-postgres/` destroys local data. Never erase it automatically or switch major images on an existing cluster. Persistence is not backup. For a logical backup:

```sh
mkdir -p /tmp/engineering-library-backups
# Uses the container's configured user and database; does not print its password.
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > /tmp/engineering-library-backups/library.dump
# Review a dump before restoring; restore into a separate empty database first.
docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" engineering_library_restore'
docker compose exec -T postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d engineering_library_restore --no-owner --exit-on-error' < /tmp/engineering-library-backups/library.dump
```

Keep backups outside the data directory and repository, protect access and verify restoration. Copying a live PGDATA folder is not a consistent backup strategy. Use logical dump/restore or documented PostgreSQL upgrade tools for major upgrades.

## Verification

```sh
docker compose config --quiet
docker compose build
docker compose up -d --wait --wait-timeout 300
docker compose exec backend bin/rails db:prepare catalog:sync
docker compose exec -e RAILS_ENV=test backend bin/rails db:prepare
docker compose exec -e RAILS_ENV=test backend bin/rails test
docker compose exec backend bin/rails zeitwerk:check
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec frontend npm run build
curl --fail http://localhost:3098/up
curl --fail http://localhost:3099
python3 -B -m unittest discover -s tools -p test_check_docs.py -v
```

The Rails suite exercises HTTP health, absence of password disclosure and a real SQL connection. Frontend lint/type/build checks are appropriate for this static scaffold; no extra browser-test library is installed. `/up` is liveness, not a full infrastructure readiness contract. Future milestone: define a first read-only collection/chapter API and render existing documentation while preserving its source and bilingual navigation. AI capabilities remain future work.

## Dependency audit limitation

ESLint 9.39.5 is retained because the React lint plugins bundled by eslint-config-next do not declare ESLint 10 compatibility. npm marks ESLint 9 as unsupported. npm audit reports five high-severity development-tool findings along the eslint-config-next → fast-glob → micromatch → braces chain; braces 3.0.3 is still the published latest release. No unsupported override or framework downgrade was applied. Revisit when upstream publishes compatible fixes. These findings are in lint tooling; runtime audit is checked separately.

## Executed validation — 2026-10-18

Validated on macOS ARM64 with Docker Desktop: Compose parses; both application images build; all three services reach healthy state; Rails database preparation/migration and Zeitwerk checks pass; Rails tests pass (2 tests, 4 assertions); Next.js lint, TypeScript and optimized webpack build pass. HTTP checks confirm `/up`, rendered landing content and server-side API connectivity. PostgreSQL authentication through the host-published port succeeds; cluster identity survives forced container recreation. Bundler install and npm ci succeed with physical host dependency directories. Credential policy, mode 0600 and non-overwriting environment initialization were checked. Runtime npm audit reports zero vulnerabilities; full audit reports the five development-tool findings described above.

The 22 existing Python validator tests pass. The six-repository documentation scan reports two pre-existing errors for an empty unknown `rust-event-relay/docs/pt-BR/manual` category and 18 blocked-link warnings; none of the errors concern Engineering Library. Of 48 original library documents, 46 remain byte-identical and the two language indexes only gain an appended navigation link. Existing README content is retained with added application guidance. DBeaver GUI interaction, visual browser inspection, Linux/x86 execution, actual missing-gem reconstruction and backup restoration were not exercised. TCP SQL authentication verifies the connection path used by desktop clients, not the DBeaver GUI itself.


[ENV](../env/index.md) · [Database migration / Migração do banco](../operations/database-migration.md)
