# Development Docker environment

[English](runtime.md) | [Português](../../pt-BR/docker/runtime.md)

## Identity and configuration

Compose project: `payment-reconciliation-lab`. Services remain `db`, `backend`, `frontend`, with generated container names, a default network and generated application image names. Development override images use the same prefix and `:development`. Maven BuildKit cache: `payment-reconciliation-lab-maven`. Backend image title and Spring application name use the new identity; its runtime user is `app`, retaining configurable UID/GID. Java packages and the catalog UI remain legacy implementation details pending domain retirement. Applied Flyway migrations are unchanged.

| Variable | Purpose / default |
| --- | --- |
| APP_ENV | `dev` in Compose; enables local OpenAPI |
| POSTGRES_DB / POSTGRES_USER | `payment_reconciliation_lab` for newly initialized databases |
| POSTGRES_PASSWORD | Required local secret |
| POSTGRES_VOLUME_NAME | `payment-reconciliation-lab_db_data` for fresh environments; exact inspected volume for existing data |
| POSTGRES_HOST_PORT / BACKEND_HOST_PORT / FRONTEND_HOST_PORT | Loopback listeners: 5432 / 8080 / 4200 |
| ALLOWED_ORIGINS | Explicit comma-separated browser origins |
| DEV_SEED_ENABLED | `false`; true fails startup until reconciliation fixtures exist |
| APP_UID / APP_GID | Backend runtime user IDs, 10001 |
| DB_URL | Host backend override; Compose uses `db:5432` and POSTGRES_DB |
| API_PROXY_TARGET | Compose supplies `http://backend:8080`; browser uses relative `/api` |
| STRIPE_SECRET_KEY | Empty reserved local setting, currently unused; no SDK or Stripe bindings exist |

Purchase-discount configuration, policy, validation and tests are removed. Catalog bootstrap SQL and runner are removed. Existing products are preserved; no reconciliation seed is claimed. Stripe variable names cannot yet be verified against an implementation. Before adding integration, bind and validate the reserved server-side test key and introduce only settings actually needed by that implementation. Never send it to Angular, copy real values to examples, print resolved environment values or commit `.env`.

The actual local `.env` was updated while retaining the initialized database's connection names/password, ports, origins, profile and UID/GID. Git ignores `.env`. `COMPOSE_PROJECT_NAME` was absent from the inspected local file and shell; repository commands contain no `-p` override except the explicit old-project stop below. An exported `COMPOSE_PROJECT_NAME` or `docker compose -p NAME` takes precedence over top-level `name`; `COMPOSE_FILE` can also change which files are loaded. Check your shell and automation before running commands. New project names do not rename old containers or volumes.

## Preserve an initialized database

The 2026-10-09 inspection found project `aurora-bakery`, containers `aurora-bakery-{db,backend,frontend}-1`, and the actual named volume `aurora-bakery_db_data` mounted at `/var/lib/postgresql/data`. Its initialized database and role are `aurora_bakery`; there are three product records and two successful Flyway migrations. The legacy `.dockerized-postgres` directory is not the inspected active mount; leave it untouched.

Use the external-volume override for this transition. It refuses to create an empty replacement if the specified volume is missing. For another installation, inspect its actual mounts rather than assuming these names. Retain its existing POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD in `.env`, and set POSTGRES_VOLUME_NAME to the inspected volume. Changing initialization variables does not rename an existing database/role. No database/role rename or data migration is needed for volume reuse.

```sh
# Read-only inventory; do not print Config.Env or full compose config.
docker compose ls
docker ps -a --filter label=com.docker.compose.project=aurora-bakery
docker inspect aurora-bakery-db-1 --format '{{json .Mounts}}'
# In your shell: remove naming/file-selection overrides for these commands.
unset COMPOSE_PROJECT_NAME COMPOSE_FILE
# Validate without revealing secrets; build before stopping the old application.
docker compose -f docker-compose.yml -f compose.existing-db.yaml config --quiet
docker compose -f docker-compose.yml -f compose.existing-db.yaml build backend frontend
# Quiesce application writes; then create a logical backup outside Git.
docker compose -p aurora-bakery -f docker-compose.yml stop frontend backend
mkdir -p /tmp/payment-reconciliation-lab-backups
# Protect backup contents; retain and verify the backup before switching.
(umask 077; docker exec aurora-bakery-db-1 sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > /tmp/payment-reconciliation-lab-backups/before-transition.dump)
# Stop old DB BEFORE attaching its volume to the new DB.
docker compose -p aurora-bakery -f docker-compose.yml stop db
docker compose -f docker-compose.yml -f compose.existing-db.yaml up -d --wait --wait-timeout 180
```

Do not run two database containers with this data volume. Stop the old services before starting new services on the same ports. Never delete volumes, use volume-removing shutdown flags or prune resources. Old stopped containers and images may remain safely. The external override can be combined after the base file and before `compose.development.yaml`; the development override disables Flyway and readiness healthchecking, so it requires an already initialized schema and manual readiness verification.

## Runtime checks and rollback

```sh
docker compose -f docker-compose.yml -f compose.existing-db.yaml ps
docker inspect payment-reconciliation-lab-db-1 --format '{{json .Mounts}}'
docker compose -f docker-compose.yml -f compose.existing-db.yaml exec -T db sh -c \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT current_database(), current_user; SELECT count(*) FROM products; SELECT count(*) FROM flyway_schema_history WHERE success;"'
curl --fail http://localhost:8080/actuator/health/readiness
curl --fail http://localhost:4200/api/v1/products
# Stop new services before rollback; then restart the retained old containers.
docker compose -f docker-compose.yml -f compose.existing-db.yaml stop frontend backend db
# Run only if rollback is needed:
docker start aurora-bakery-db-1
# Wait for DB health before starting backend; wait for readiness before frontend.
docker start aurora-bakery-backend-1
docker start aurora-bakery-frontend-1
```

Compare preserved rows and migration history with the baseline, not merely container health. Base frontend depends on backend health inherited from the runtime Dockerfile. That healthcheck requests `/actuator/health/readiness`; readiness includes DB connectivity. Base DB and frontend also have healthchecks. No duplicate backend Compose healthcheck is needed. The development override deliberately uses `service_started` and disables the backend healthcheck.

For fresh environments use [setup](../guides/setup.md) without the external-volume override, after setting a local password. For dependency recovery see [development setup](development.md). Current test evidence is recorded in [verification](../testing/verification.md); previous audit results are historical.
