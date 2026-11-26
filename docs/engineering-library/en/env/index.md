# Environment and configuration

[Project index](../index.md) · [Configuration contract](configuration-contract.md)

Reviewed from public declarations on 2026-11-26. Local `.env`, management keys and effective container environments are not documentation inputs. Examples intentionally contain no credentials. Shell variables can override Compose interpolation; never print an effective secret-bearing configuration into an issue.

<!-- reading-section: index-1 -->
## Compose and application inputs

| Variable | Consumer and default | Important behavior |
| --- | --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | PostgreSQL initialization and Rails connection | Compose rejects missing/empty values; initialization does not rotate an existing cluster's credentials. |
| `SECRET_KEY_BASE` | Rails | Compose rejects missing/empty values; keep private. |
| `POSTGRES_PORT`, `BACKEND_PORT`, `FRONTEND_PORT` | Loopback host bindings: `5499`, `3098`, `3099` | Missing or empty values use defaults; internal ports stay 5432/3000/3000. |
| `LOCAL_UID`, `LOCAL_GID` | Backend/frontend user: `1000:1000` | New Linux environment generation uses current UID/GID; existing environment is preserved. |
| `WATCHPACK_POLLING` | Frontend development watcher: `1000` | Compose supplies default for missing/empty. |
| `CATALOG_ROOT`, `DOCUMENTATION_ROOT` | Rails catalog and Next reader: `/docs` in Compose | Root of all project collections, not one language/project folder. |
| `BACKEND_URL` | Next server: `http://backend:3000` | Internal service address; an explicitly empty direct-execution value is not a usable fallback. |
| `POSTGRES_HOST` | Rails: `postgres` | DB configuration fixes internal port 5432; it does not consume the published host port. |
| `RAILS_MAX_THREADS` | Rails DB pool/Puma | DB configuration default is 5; Puma default is 3. Review both before tuning. |
| `DOCS_HOST_REQUIRED` | Backend: `1` in Compose | Requires adapter at startup and in `/up`; not a production authentication control. |
| `OLLAMA_NO_CLOUD` | Ollama: `1` in Compose | Local runtime policy; no default published Ollama port. |

Direct process execution is not identical to Compose interpolation. Ruby/JavaScript environment lookups often retain an explicitly empty string, while `${NAME:-default}` uses a default for missing or empty values. Production `DATABASE_URL` exists in Rails configuration, but the supplied stack runs development; its presence does not establish a production deployment procedure.

<!-- reading-section: index-2 -->
## Default documentation caller

These inputs are consumed by `Documentation::Command`. A host shell export does not automatically enter an already running backend container, and CLI-only overrides do not change frontend jobs. They describe existing controls, not a recommendation to modify the approved model or agent configuration.

| Variable | Default | Accepted range or behavior |
| --- | --- | --- |
| `DOCS_MODEL` | `llama3.2:3b` | Must match approved manifest identity and Ollama digest. |
| `DOCS_OLLAMA` | `http://ollama:11434` | Existing local service endpoint. |
| `DOCS_CONTEXT` | `skills` | `skills` or explicit `baseline`; normal path loads three approved skills. |
| `DOCS_TRANSPORT` | `chat` | `chat` or `generate`. |
| `DOCS_EVIDENCE_MODE` | `declarations` | `raw`, `declarations` or `structural`; validation differs by mode. |
| `DOCS_CONTEXT_TOKENS` | `16384` | Integer 4096–16384. |
| `DOCS_MODEL_THREADS` | Unset | Optional integer 1–16. |
| `DOCS_REQUEST_TIMEOUT` | `1800` seconds | Integer 60–1800; automatic per-declaration requests share the overall deadline. |
| `DOCS_FACT_LIMIT` | `4` | Integer 1–5; bounded summary, not chapter count or full coverage. |
| `DOCS_RESEARCH` | `offline` | Optional research is separate; do not infer automatic internet/RAG use. |
| `DOCS_LIBRARY`, `DOCS_AGENT`, `DOCS_SOURCES`, `DOCS_DESTINATIONS` | `/docs`, `/agent`, `/sources`, `/project-docs` | Container defaults; source/destination selection also respects catalog/config and host snapshots. |
| `DOCS_HOST_EXCHANGE` | Main deployment's private `filesystem/host` exchange | Internal shared directory; do not replace with arbitrary public paths. |
| `DOCS_HOST_DEFER_DELIVERY` | Unset | Coordinator sets `1` for child generation and performs host delivery itself. |

The host worker has separate bounded acquisition inputs: `DOCS_HOST_FILE_BYTES` (32 MiB, maximum 128 MiB), `DOCS_HOST_SOURCE_BYTES` (512 MiB, maximum 8 GiB), `DOCS_HOST_DOCS_BYTES` (128 MiB, maximum 1 GiB), `DOCS_HOST_ENTRIES` (200,000, maximum 2,000,000) and `DOCS_HOST_FILES` (100,000, maximum 200,000). All must be positive. They are read by the host worker, not the model or browser. Changing a variable in a container does not configure that host process.

<!-- reading-section: index-3 -->
## Safe installation example

```sh
# Existing helper creates private .env only when absent, then starts managed runtime.
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
```

The launcher is not a secret-rotation tool. Do not overwrite an existing environment, delete the database or replace model/skill resources to make startup pass. See [development](../guides/application-development.md), [MakeDocs](../training/local-documentation-command.md) and [recovery](../operations/runtime-and-recovery.md).

Sources: `.env.example`, `compose.yaml`, `backend/config/database.yml`, `backend/config/puma.rb`, `backend/lib/documentation/command.rb`, `backend/lib/documentation/host_filesystem.rb`, `frontend/lib/catalog.ts`, `tools/init_dev_env.py` and `tools/host_filesystem.py`.
