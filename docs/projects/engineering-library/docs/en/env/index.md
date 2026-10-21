# ENV — engineering-library

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

## Docker Compose inputs

Each row describes behavior **at Compose interpolation**, before the application. `:-` uses the default for both missing and empty values; `:?` rejects both. An empty default is intentionally permitted at this layer. Final consumer behavior is described below.

[Source configuration](../../../../../../compose.yaml)

| Variable | Responsibility / consumer | Required | Missing | Empty | Safe example / default | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `POSTGRES_USER` | PostgreSQL connection and initialization / database and backend | yes | Compose error | Compose error | `Set POSTGRES_USER` | L6 |
| `POSTGRES_PASSWORD` | PostgreSQL connection and initialization / database and backend | yes | Compose error | Compose error | `<secret>` | L7 |
| `POSTGRES_DB` | PostgreSQL connection and initialization / database and backend | yes | Compose error | Compose error | `Set POSTGRES_DB` | L8 |
| `POSTGRES_PORT` | Network port / Compose and corresponding service | no | default | default | `5499` | L11 |
| `LOCAL_UID` | File ownership / build or container user | no | default | default | `1000` | L21 |
| `LOCAL_GID` | File ownership / build or container user | no | default | default | `1000` | L21 |
| `SECRET_KEY_BASE` | secret key base | yes | Compose error | Compose error | `<secret>` | L28 |
| `BACKEND_PORT` | Network port / Compose and corresponding service | no | default | default | `3098` | L37 |
| `FRONTEND_PORT` | Network port / Compose and corresponding service | no | default | default | `3099` | L59 |

## Consumers and differences outside Compose

| Variable | Consumer | Missing / default | Empty (direct execution) | Source |
| --- | --- | --- | --- | --- |
| `POSTGRES_HOST` | Rails DB | postgres | empty host passed to adapter; no ENV fallback | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_USER` | Rails DB | KeyError | empty username passed; authentication may fail | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_PASSWORD` | Rails DB | KeyError | empty password passed; not supported by Compose | [database.yml](../../../../../../backend/config/database.yml) |
| `POSTGRES_DB` | Rails DB | KeyError | empty database passed; not supported by Compose | [database.yml](../../../../../../backend/config/database.yml) |
| `RAILS_MAX_THREADS` | Rails/Puma | DB pool 5; Puma 3 | empty string retained; not a valid intended thread count | [puma.rb](../../../../../../backend/config/puma.rb) |
| `PORT` | Puma | 3000 | empty string retained; CLI -p 3000 overrides in Docker | [puma.rb](../../../../../../backend/config/puma.rb) |
| `PIDFILE` | Puma | not set | Ruby treats empty string as truthy; empty path passed | [puma.rb](../../../../../../backend/config/puma.rb) |
| `DATABASE_URL` | Rails production | nil; shared config remains | empty URL retained in ERB; adapter resolution not verified | [database.yml](../../../../../../backend/config/database.yml) |
| `BACKEND_URL` | Next server catalog API | http://backend:3000 | empty is retained; fetch fails and catalog shows unavailable | [frontend/lib/catalog.ts](../../../../../../frontend/lib/catalog.ts) |
| `SECRET_KEY_BASE` | Rails / Compose | Compose error | Compose error; use generated secret, never publish | [compose.yaml](../../../../../../compose.yaml) |
| `CI` | Rails tests | eager_load false | present? false; nonblank enables eager loading | [environments/test.rb](../../../../../../backend/config/environments/test.rb) |
| `RAILS_ENV` | Rails runtime | Compose sets development | direct execution outside Compose: framework behavior not verified | [compose.yaml](../../../../../../compose.yaml) |
| `BUNDLE_GEMFILE` | Ruby boot | backend/Gemfile | Ruby ||= retains empty; invalid file selection possible | [boot.rb](../../../../../../backend/config/boot.rb) |

Variables without a required marker are optional. Empty host/user/database values have no Ruby fallback and may cause connection failure. Empty numeric settings are not supported. Production adapter URL resolution requires separate validation.

`POSTGRES_PORT=5499` is host-only; Rails uses `postgres:5432`. Compose fixes `BACKEND_URL=http://backend:3000`, `RAILS_ENV=development`, `CATALOG_ROOT=/docs/projects` (Rails), `DOCUMENTATION_ROOT=/docs/projects` (Next.js), `PGDATA=/var/lib/postgresql/18/docker`, `HOME=/tmp`, `BUNDLE_PATH=/usr/local/bundle`, `BUNDLE_APP_CONFIG=/tmp/bundle-config`, `npm_config_cache=/tmp/npm-cache` and `NEXT_TELEMETRY_DISABLED=1`; these are not new `.env` inputs. Dependency/cache directories must be writable. Next fetches server-side, so CORS needs no change. `POSTGRES_DB` only initializes databases in fresh clusters. See [migration](../operations/database-migration.md).

## Catalog filesystem roots — 2026-10-19

`CATALOG_ROOT` optionally selects the Rails catalog directory; default is `../docs/projects` relative to Rails root. `DOCUMENTATION_ROOT` selects the Next collection; default is the same sibling path relative to its working directory. Compose fixes the latter to `/docs/projects` and keeps that collection read-only in Rails and writable in frontend for explicit maintenance. An empty override is retained rather than replaced by the default; use a valid explicit directory or leave it absent. These paths must refer to the same intended public collection. They do not authorize runtime reads of sibling source repositories. `BACKEND_URL` is server-side catalog access with a five-second timeout; `/up` liveness has a separate contract.

In the existing frontend, Compose sets `BROWSER_BASE_URL=http://localhost:3000` and `BOOK_READER_URL=http://localhost:3000`. The image sets `PLAYWRIGHT_MODULE=/opt/browser/node_modules/playwright` and `PLAYWRIGHT_BROWSERS_PATH=/opt/playwright`. `PLAYWRIGHT_EXECUTABLE_PATH` is only needed to select another executable inside the container. These variables require no host Node or browser installation.
