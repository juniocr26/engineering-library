# Docker development setup and recovery

Run every command below from the host `payment-reconciliation-lab/` directory. Docker Engine/Desktop and Docker Compose are required; the previous dependency audit used Compose v5.1.4 on macOS. Images pin Node 22.23.3 (npm 10.9.9), Java 25.0.4.1 and PostgreSQL 17.11. The tracked Maven wrapper installs Maven 3.9.11; Angular is 21.2.x. No host npm or Maven installation is required.

## Services and safety

`db` is PostgreSQL; `backend` is Spring Boot/JPA/Flyway; `frontend` is Angular with an API proxy to `backend:8080`. Project name remains `payment-reconciliation-lab`. Default host ports are 5432, 8080 and 4200 on loopback. The base backend runs Flyway migrations automatically and rejects the retired seed flag when enabled. Do not start it against existing data during a dependency audit.

The frontend waits for backend process startup rather than health in this override; readiness still needs manual verification. The explicit development override uses a JDK/Maven source workspace and an Angular source bind mount. It disables Flyway and keeps the retired seed flag false. The runtime Dockerfile still packages a JAR and uses the existing JRE entrypoint. Development images have separate tags. Existing database data is untouched.

## Fresh clone and dependency installation

```sh
# Create configuration only if absent; then edit locally with your own values.
if [ ! -e .env ]; then cp .env.example .env; fi
# Set POSTGRES_PASSWORD; ensure DEV_SEED_ENABLED=false.
mkdir -p backend/.m2
docker compose -f docker-compose.yml -f compose.development.yaml build backend frontend
docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh frontend -c 'npm ci --no-fund'
docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh backend -c 'sh ./mvnw -B -ntp compile -DskipTests'
```

These setup containers publish no ports, skip service dependencies and never launch Spring. Maven compilation does not execute tests. `npm ci` uses the existing lockfile; it replaces the installation directory. The repository's npm scripts have no install-time application startup hook.

| Component / manager | Container path | Physical host path relative to project | Mount | Purpose |
| --- | --- | --- | --- | --- |
| Angular / npm | `/app/node_modules` | `frontend/node_modules` | Source directory bind | Installed JS and Linux native packages |
| Java / Maven wrapper | `/root/.m2/repository` | `backend/.m2/repository` | Bind | Local dependency/plugin repository |
| Maven wrapper | `/root/.m2/wrapper` | `backend/.m2/wrapper` | Same bind | Downloaded Maven distribution |

npm's `/home/node/.npm` download cache is disposable container storage; it is not the installed dependency directory. `backend/target`, `frontend/.angular`, `frontend/dist` and `frontend/out-tsc` are build artifacts, not dependency backups. Maven downloads JARs and plugins into its native repository rather than a project `vendor` directory. Custom `settings.xml` in `.m2` is configuration, not a reproducible download.

## Safe startup and shutdown

A dependency-only setup needs no persistent application containers. To preview resolved mounts without printing environment values:

```sh
docker compose -f docker-compose.yml -f compose.development.yaml config --services
docker ps --format '{{.Names}} {{.Ports}}'
```

Angular can run alone (its API proxy will be unavailable):

```sh
docker compose -f docker-compose.yml -f compose.development.yaml up -d --no-deps frontend
docker compose -f docker-compose.yml -f compose.development.yaml stop frontend
```

Full startup requires an already initialized, compatible database schema. With Flyway disabled the development backend cannot initialize a fresh schema. Database initialization/migration is an explicit operation outside this safe dependency guide. The earlier dependency audit did not verify full startup; see [current validation](../testing/verification.md). After schema readiness, use `docker compose -f docker-compose.yml -f compose.development.yaml up -d`; this starts the database and backend and can expose application writes. Stop only services you started with `docker compose -f docker-compose.yml -f compose.development.yaml stop frontend backend db`. Never remove volumes to recover dependencies.

## Deleted dependencies and stopped containers

Stop your running frontend before reinstalling node_modules; stop your backend before restoring its Maven repository. Recreate missing directories with `mkdir -p backend/.m2`, then rerun the corresponding one-off installation commands above. They work when application containers exit immediately. No image rebuild is needed for deleted host dependencies. Recreate an existing service container with `up -d --no-deps --force-recreate frontend` (with both Compose files) if its previous mount referred to a deleted/recreated directory. Do not recreate the backend until its database startup is safe. Rebuild only when Dockerfile/toolchain changes require it.

## Configuration recovery

For a missing `.env`, use the guarded template copy above; deleted custom passwords/settings require a backup or your secret source. Template defaults do not restore custom values. Missing tracked Dockerfiles, Compose files, `backend/.mvn`, `mvnw`, POM, Angular JSON/TypeScript/proxy files, manifests or lockfiles can be restored individually with `git restore --source=HEAD -- path/to/missing-file`, only after confirming that path is absent and no wanted edits will be lost. Restore the wrapper directory from Git, not dependency installation. No application-generated configuration directory was identified. Maven can redownload `.m2/repository` and `.m2/wrapper`; custom `.m2/settings.xml` requires backup. Deleted PostgreSQL data/configuration in persistent storage requires backup recovery; never substitute an empty directory or template as recovery.

## Troubleshooting

Always specify both Compose files. Base Compose alone uses image dependencies and a packaged backend, so it does not meet host dependency persistence. Inspect mounts with `docker inspect CONTAINER --format '{{json .Mounts}}'`; a volume over node_modules would hide the host installation. On Linux, the frontend's `node` user must be able to write its source bind mount; use a one-off `--user "$(id -u):$(id -g)" -e HOME=/tmp` if needed and inspect ownership of the specific generated directory. The Maven development image uses root; use a matching host UID with HOME and Maven user home pointing to writable locations if root ownership is a problem. Do not use chmod 777 or broad recursive permission changes.

For a port conflict, inspect Docker listeners and the host's listening processes; stop only your own audit services or choose unused `FRONTEND_HOST_PORT`, `BACKEND_HOST_PORT`, `POSTGRES_HOST_PORT` values in local configuration. Update allowed origins when changing the frontend port. Container-installed native packages are Linux/platform-specific and should be used inside these containers, not executed directly on macOS/Windows. Lockfiles and toolchain versions remain unchanged.

## Verification (2026-10-06)

Originally npm packages lived in an image and Maven downloads in a BuildKit cache. Resolved development mounts were inspected. `npm ci --no-fund` succeeded (466 packages); Angular resolved from `/app/node_modules/@angular/core/fesm2022/core.mjs`, which physically exists under host `frontend/node_modules`. A second fresh one-off container resolved the same host installation without reinstalling. npm reported three dependency vulnerabilities; no upgrades were performed. Maven `compile -DskipTests` succeeded, compiling 12 Java files. A fresh container also completed offline compilation using host `backend/.m2`. The physical host PostgreSQL JAR and downloaded Maven distribution were checked. `dependency:go-offline` was stopped after transitive repository traversal stalled (including a GitHub Packages 401); complete offline coverage for every plugin/test dependency remains unverified. Use the tested compile command for normal restoration, with online Maven goals resolving additional dependencies as needed. No existing dependency directory was deleted or renamed. Empty-directory Angular recovery succeeded using a separate temporary host bind at `/app/node_modules`; host files were confirmed and that temporary directory was removed. Maven empty-cache recovery was not separately simulated; its newly created project-local cache was populated during this audit. Application/DB startup was not performed. No databases, tests, migrations, seeders or external integrations were executed.

## Copyable host verification and tracked configuration recovery

```sh
# Host project root; existence checks do not modify dependencies.
test -f frontend/node_modules/@angular/core/fesm2022/core.mjs
test -f backend/.m2/repository/org/postgresql/postgresql/42.7.12/postgresql-42.7.12.jar
# Restore only absent tracked configuration files; preserve existing edits.
for path in .env.example docker-compose.yml backend/Dockerfile backend/pom.xml backend/mvnw backend/.mvn/wrapper/maven-wrapper.properties frontend/Dockerfile frontend/package.json frontend/package-lock.json frontend/angular.json frontend/proxy.conf.cjs frontend/tsconfig.json frontend/tsconfig.app.json frontend/tsconfig.spec.json; do
  if [ ! -e "$path" ]; then git restore --source=HEAD -- "$path"; fi
done
```

Check that the override and this guide are tracked; protect local edits in a working-tree backup. Maven compile regenerates target; Angular build regenerates dist and build cache using `docker compose -f docker-compose.yml -f compose.development.yaml run --rm --no-deps -T --entrypoint npm frontend run build`. That Angular build command is derived from the script and was not run. The base backend/runtime and Angular development image builds were also validated successfully, reusing cached Maven package layers; this does not verify host-cache coverage for all Maven goals. No audit containers or temporary test directories remain.
