# Application development

## Docker execution

Run shell commands from this repository root. Node.js, npm, Ruby, Bundler, Rails and PostgreSQL clients execute inside containers; the host needs Docker with Compose. No host installation of these runtimes is required. `exec` requires a running service and uses `/app/frontend` or `/app/backend`; Build verification copies source into a temporary directory inside the existing frontend container to preserve the running server cache.

For bootstrap, copy `.env.example` to `.env` and fill in private credentials, or use the optional host Python generator below; existing `.env` is preserved by the generator. Host Python 3.10+ is an optional exception: `python3 tools/init_dev_env.py` generates credentials; documentation validators use only the standard library; `tools/check_docker_startup.py` orchestrates Docker and probes host ports. Install Python only if choosing those host tools. Its presence is not assumed.

Playwright 1.58.2, Chromium and system dependencies are installed in `frontend-development`, outside the application dependency target. Rebuild with `docker compose up -d --build --wait --wait-timeout 300`. Browsers running in frontend access `http://localhost:3000`, the same container's internal port; host browsers use `http://localhost:3099`. Other containers use `http://frontend:3000`. Demo scripts remain restricted to loopback.

Other catalog projects document their source repositories, rather than operational commands for this installation; this policy does not claim additional Docker support for those projects. Older validation results are historical.


Current review: 2026-10-19. Rails serves the PostgreSQL-backed catalog and shared annotations; Next renders the bilingual internal book. The setup below retains its development scope; see [current architecture](../architecture/current-state.md) and [reader guide](book-frontend.md) for present responsibilities.

## Versions and architecture

Ruby 3.4.11, Rails 8.1.4, PostgreSQL 18 (official `18-bookworm` major-pinned image), Node 24.22.0, Next.js 16.4.2, React 19.3.1, TypeScript 5.9.3, ESLint 9.39.5. Gemfile.lock and package-lock.json pin dependencies. PostgreSQL minor image updates are intentional; this development environment is not a production deployment.

Browser :3099 → Next.js :3000 → Rails :3000 on Compose → PostgreSQL :5432. Rails is also exposed on loopback :3098. Next catalog requests use server-side `BACKEND_URL`, `cache: no-store` and a five-second timeout. Rails `/up` remains boot liveness, not a catalog/database query. Current services/models implement catalog sync, pagination and shared annotations; the reader also implements page-turn transitions. There is no account authentication, AI inference or automatic documentation-generation pipeline. Browser API access uses same-origin Next routes; the reviewed Rails CORS initializer is inactive.

```text
docker/
  Dockerfile              backend-dependencies, backend-development,
                          frontend-dependencies, frontend-development
  backend-entrypoint.sh   db:prepare catalog:sync; exec Rails
  frontend-entrypoint.sh  lockfile consistency; exec Next.js
backend/                  Rails, Gemfile.lock
frontend/                 Next.js, package-lock.json
docs/                     Markdown
.dockerized-postgres/     PostgreSQL 18: 18/docker
.env                      local credentials (ignored)
compose.yaml              PostgreSQL + independent Rails and Next.js services
```

## Setup and lifecycle

Install Docker Desktop on macOS or Docker Engine with the Compose plugin on Linux using the [official installation guide](https://docs.docker.com/engine/install/). Enable the engine, allow project file sharing, and ensure ports 3099, 3098 and 5499 are free. No host Ruby or Node installation is needed.

The initial implementation generated `.env` locally with an ASCII alphanumeric 12-character database password containing upper/lowercase letters and digits, and a random Rails secret. Neither is committed. On a fresh clone use the optional Python bootstrap below or prepare `.env` manually; it creates `.env` without replacing an existing file. Host Python 3.10+ is an optional alternative. The example lists all variables. On Linux set LOCAL_UID and LOCAL_GID to `id -u` and `id -g` before installing dependencies. macOS Docker Desktop supports the default 1000 IDs. Keep the bind-mounted source and dependency folders writable by these IDs. If previously created files belong to another ID, adjust ownership deliberately; do not recursively change PostgreSQL ownership to your app user. The official postgres entrypoint manages its own data ownership.

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# Open http://localhost:3099 and http://localhost:3098/up
# Stop, preserving all bind-mounted data:
docker compose down
```

PostgreSQL creates the database on first cluster initialization. Rails waits for healthy PostgreSQL, runs `db:prepare catalog:sync`, then starts serving; preparation failures stop the process. Next waits for healthy Rails. Review future migrations before startup. The current sync updates metadata without deleting records.

The sole Dockerfile uses the root context and four targets: `backend-dependencies`, `backend-development`, `frontend-dependencies` and `frontend-development`. Gems live in `/usr/local/bundle`; Node packages in `/app/node_modules`, above source mounted at `/app/frontend`. An empty `node_modules` mount masks host packages. `.next`, Rails logs and temporary files use tmpfs and are discarded on stop. Lockfile dependencies install during build, with no installation or registry access at startup. Services run as LOCAL_UID/LOCAL_GID, default 1000:1000. These are development images.

## Dependencies and commands

```sh
docker compose build backend
docker compose build frontend
# After updating manifests and lockfiles:
docker compose up -d --build
# Next build isolated from the running development server's cache:
docker compose exec -T frontend npm run build:check
docker compose exec backend bin/rails console
docker compose logs -f backend frontend postgres
# Five controlled cycles; preserves data and leaves the final cycle running:
python3 tools/check_docker_startup.py --cycles 5
```

Update lockfiles using the package managers inside the existing containers, then rebuild the corresponding image. Dependencies installed only in a running container are not reproducible. Old host packages and gems remain intact but are unused. Next's tmpfs cache uses memory and recompiles after container stop. Do not run `npm run build` inside the live development server: use the isolated command above.

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
docker compose exec -T frontend npm run build:check
curl --fail http://localhost:3098/up
curl --fail http://localhost:3099
python3 -B -m unittest discover -s tools -p test_check_docs.py -v
```

The Rails suite exercises HTTP health, absence of password disclosure and a real SQL connection. Frontend unit/lint/type/build checks run in Docker; development images also include Playwright and Chromium for the documented browser suites. `/up` is liveness, not a full infrastructure readiness contract. Future milestone: define a first read-only collection/chapter API and render existing documentation while preserving its source and bilingual navigation. AI capabilities remain future work.

## Dependency audit limitation

ESLint 9.39.5 is retained because the React lint plugins bundled by eslint-config-next do not declare ESLint 10 compatibility. npm marks ESLint 9 as unsupported. npm audit reports five high-severity development-tool findings along the eslint-config-next → fast-glob → micromatch → braces chain; braces 3.0.3 is still the published latest release. No unsupported override or framework downgrade was applied. Revisit when upstream publishes compatible fixes. These findings are in lint tooling; runtime audit is checked separately.

## Executed validation — 2026-10-18

Validated on macOS ARM64 with Docker Desktop: Compose parses; both application images build; all three services reach healthy state; Rails database preparation/migration and Zeitwerk checks pass; Rails tests pass (2 tests, 4 assertions); Next.js lint, TypeScript and optimized webpack build pass. HTTP checks confirm `/up`, rendered landing content and server-side API connectivity. PostgreSQL authentication through the host-published port succeeds; cluster identity survives forced container recreation. Bundler install and npm ci succeed with physical host dependency directories. Credential policy, mode 0600 and non-overwriting environment initialization were checked. Runtime npm audit reports zero vulnerabilities; full audit reports the five development-tool findings described above.

The 22 existing Python validator tests pass. The six-repository documentation scan reports two pre-existing errors for an empty unknown `rust-event-relay/docs/pt-BR/manual` category and 18 blocked-link warnings; none of the errors concern Engineering Library. Of 48 original library documents, 46 remain byte-identical and the two language indexes only gain an appended navigation link. Existing README content is retained with added application guidance. DBeaver GUI interaction, visual browser inspection, Linux/x86 execution, actual missing-gem reconstruction and backup restoration were not exercised. TCP SQL authentication verifies the connection path used by desktop clients, not the DBeaver GUI itself.


[ENV](../env/index.md) · [Database migration / Migração do banco](../operations/database-migration.md)

## Validation of this change — 2026-10-21

In existing services: 100 frontend tests, lint and TypeScript passed; `build:check` completed in a temporary directory inside frontend, preserving the server cache. Rails passed 25 tests and 408 assertions in the `_test` database. The demo regression passed using a synthetic database in the existing PostgreSQL, idempotent seeds, two browsers and cleanup preserving manual annotations. CLI setup and cleanup also passed, preserving two synthetic notes in different projects. The backend was restored to the original database; hashes and counts of 60 notes, 60 highlights and 12 bookmarks matched before/after. The temporary database was removed.

Chromium ran inside frontend; manifest: 132 valid anchors, zero invalid. The five-viewport smoke passed after an initial navigation timeout. Snapshot generation passed on a temporary documentation copy without changing published snapshots. Anchor inspection now retries a single read interrupted by navigation, without repeating mutations. The additional QA stack from the previous attempt, its Compose file and its two images were removed; only the original three services remain.

Host Python: 27 tests passed; catalog had no errors and one warning for identical IMG indexes. `npm ci` reported five existing high vulnerabilities; dependency remediation was not part of this task. The source suite that starts a fixture server failed with `width is not defined` during the previous attempt and remains outside the authorized workflow. Linux/x86 and production deployment were not validated.
