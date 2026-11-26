# Development environment and operational commands

[Guides index](index.md) · [Runtime and recovery](../operations/runtime-and-recovery.md)

<!-- reading-section: application-development-1 -->
## Prerequisites and startup

Use the existing Docker/Compose stack and Python 3.10+ on a POSIX host. Application Node.js/npm, Ruby/Bundler/Rails and PostgreSQL clients run inside containers. Python on the host is required by the managed filesystem adapter, not merely an optional credential generator. On Windows, use a WSL2 POSIX environment with Docker integration; native PowerShell does not support this adapter. Keep scripts in LF as enforced by `.gitattributes`. No Windows-host acceptance is claimed here.

Run all examples from the checkout root. Ensure Docker is available, the checkout is shared with Docker Desktop when applicable, and default loopback ports 3099, 3098 and 5499 are available. Preserve an existing `.env`; the launcher creates one with private random credentials only when absent, without printing them. On Linux it sets generated UID/GID values from the current user; an existing `.env` still needs deliberate ownership review. Never recursively assign PostgreSQL storage to the application user.

```sh
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
# Open http://127.0.0.1:3099 and http://127.0.0.1:3098/up
python3 -B tools/init_dev_env.py status
docker compose ps
# Stop and restart while preserving data:
python3 -B tools/init_dev_env.py stop
python3 -B tools/init_dev_env.py up -d
# Remove service containers/network while preserving persistent files:
python3 -B tools/init_dev_env.py down
```

Startup is not read-only. Backend startup checks dependencies, waits for the required adapter, runs `db:prepare catalog:sync` and starts Rails. Frontend waits for backend health. Review migrations before upgrading. A raw Compose start without the managed supervisor is incomplete for host-backed project operations.

<!-- reading-section: application-development-2 -->
## Services, network and storage

| Component | Address inside Compose | Default host access | Storage / boundary |
| --- | --- | --- | --- |
| Frontend Next.js | `frontend:3000` | `127.0.0.1:3099` | Frontend source/dependencies bind; `.next` tmpfs; library `/docs` writable |
| Backend Rails | `backend:3000` | `127.0.0.1:3098` | Backend source/dependencies bind; tmp/log tmpfs; library `/docs` writable |
| PostgreSQL 18 | `postgres:5432` | `127.0.0.1:5499` | `.dockerized-postgres/18/docker` |
| Ollama | `ollama:11434` | No default published port | Persistent `ollama/`, local inference, cloud disabled |
| Host adapter | Private file exchange | No HTTP port | Normal-user supervised process and private snapshots |

`docker/Dockerfile` provides separate dependency/development targets. The backend also reads `/agent` and existing source mounts; narrow self/compatibility mappings are supplied through the generated filesystem mount configuration. Ordinary external sources use the managed adapter rather than arbitrary new mounts. Do not edit generated mount metadata as a repair substitute.

Backend and frontend are independent processes communicating through HTTP, not one combined server. Browser requests go to Next's same-origin routes; server requests use `BACKEND_URL=http://backend:3000`. Host port overrides do not change service-internal ports. Local loopback bindings and development management restrictions are not a production authentication architecture.

<!-- reading-section: application-development-3 -->
## Local dependency sources (Docker development)

Physical dependency sources are installed in `frontend/node_modules` and `backend/vendor/bundle`. This supports container runtime and source inspection, but native modules belong to the container platform. Avoid replacing them with host-platform installs. Frontend startup fingerprints the runtime, manifests, entrypoint and installed npm lock, verifies dependency integrity/native bindings and reuses matching packages; otherwise it runs `npm ci --include=dev`. Backend uses the locked bundle and startup dependency checks. Build caches and lockfiles do not replace backups.

Editor indexing may see Linux dependency sources without being able to execute their binaries on macOS/Windows. Execute application tooling inside the existing container; do not install a second host runtime to make editor diagnostics appear green. The isolated build check avoids writing into the running development server's `.next` cache.

```sh
# Existing read/analysis commands; exec requires running services.
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
# Build verification writes only its isolated container build workspace.
docker compose exec -T frontend npm run build:check
# Log content is private; redact before sharing.
docker compose logs --tail=100 backend frontend postgres ollama
```

These are available operational commands, not a claim that they were run during this documentation update. Database-backed tests and demo utilities can mutate data; consult their scope before execution. Existing browser tooling is installed in the development image; no additional service or dependency installation is needed for ordinary checks.

<!-- reading-section: application-development-4 -->
## PostgreSQL access and preservation

A desktop client uses PostgreSQL host `127.0.0.1`, published port `5499` or its configured override, and the user/database from local `.env`. Read credentials privately; never paste them into documentation or command history. Rails connects internally to `postgres:5432`. Local SSL is not configured by this stack.

Initialization environment variables apply when creating a new cluster. Changing `.env` does not rotate an existing role password. Diagnose a mismatch and coordinate an authorized credential change; never delete `.dockerized-postgres/` to fix authentication. A persistent bind mount is not a backup or proof of a successful restore. Keep logical dumps private and verify restores in an explicitly authorized isolated database. The [database migration guide](../operations/database-migration.md) retains the separate major-version migration procedure.

<!-- reading-section: application-development-5 -->
## Catalog and documentation operations

Use the frontend's explicit registration, MakeDocs/update and removal actions. Paths such as `../example-project` are relative to the library checkout, not the terminal directory. Registration is idempotent and does not call the model. Removal preserves original source/docs; re-registration can restore eligible archived library content. Do not run a blanket generation command just to check health or create directories manually before first generation.

For a specifically authorized registered project, the default CLI is `docker compose exec -T backend make docs DOCS_ARGS='--project example-project'`. This writes documentation and uses the same command as the frontend. Review [MakeDocs](../training/local-documentation-command.md) and [recovery](../operations/runtime-and-recovery.md) before invoking it. Accepted publication still produces a draft requiring factual and bilingual review.

<!-- reading-section: application-development-6 -->
## Maintenance limits

Do not use `down -v`, Docker prune, database resets, model deletion or operational-state cleanup as normal shutdown. Preserve agent skills, prompts, learning evidence and recovery directories. Optional research infrastructure is not part of normal startup and should not be enabled for routine diagnosis. Current source-derived instructions supersede older startup examples; dated reports remain evidence of their original scope.

Sources: `compose.yaml`, `docker/Dockerfile`, `docker/backend-entrypoint.sh`, `docker/frontend-entrypoint.sh`, `.env.example`, `tools/init_dev_env.py`, `tools/library_runtime.py` and `frontend/package.json`.
