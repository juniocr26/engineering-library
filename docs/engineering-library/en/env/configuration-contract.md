# Configuration contract without values

Reviewed 2026-11-04 from source declarations, without opening dotenv, credentials, runtime stores or signing files. Feature-specific requirements differ from application boot requirements. An env() reference alone does not prove a variable is globally required.

| Key / input | Contract |
| --- | --- |
| `POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, SECRET_KEY_BASE` | Required by existing Compose; private installation values |
| `FRONTEND_PORT, BACKEND_PORT, POSTGRES_PORT` | Optional host bindings default 3099/3098/5499 on loopback |
| `LOCAL_UID, LOCAL_GID` | Optional development identity defaults 1000:1000; no recursive permission repair implied |
| `CATALOG_ROOT, DOCUMENTATION_ROOT` | Catalog/reader mounts; existing Compose supplies their container locations |


Use the existing setup/environment/runbook for operational changes. Never paste private values into the catalog, copy an effective environment file, or run a mutating updater as a documentation check. No environment file, variable, schema or service was changed.
