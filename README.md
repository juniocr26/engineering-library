# Engineering Library

> Private software project belonging to Viva Bem, maintained in a private repository for authorized internal use. Do not publicly disclose source code, internal documentation or project-specific information without authorization.

[English documentation](docs/engineering-library/en/index.md) · [Português brasileiro](README.pt-BR.md)

## Current implementation

Engineering Library combines a bilingual Markdown book reader, project catalog, shared PostgreSQL annotations and local Ollama documentation drafting. Next.js reads chapter files and calls Rails for catalog metadata, notes, highlights, bookmarks and guarded development management. A supervised POSIX host adapter resolves registered relative source references and publishes accepted drafts to the library and the original project documentation.

MakeDocs is operational. Its bounded generated summaries remain drafts requiring factual and bilingual review; desired writing quality, complete-project acceptance and neural fine-tuning are not established by successful publication. A future quality campaign is separate from normal operation.

## Installation and lifecycle

Use Docker with Compose and host Python 3.10+ in a POSIX environment. Application Node.js, Ruby, Rails and database clients run inside containers. On Windows use WSL2 with Docker integration; native PowerShell cannot run the current adapter. Run from this checkout root:

```sh
# Preserves existing .env; generates private credentials only if absent.
# Starts the required host supervisor and the existing Compose services.
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
# Frontend: http://127.0.0.1:3099
# Backend health: http://127.0.0.1:3098/up
python3 -B tools/init_dev_env.py status
python3 -B tools/init_dev_env.py stop
python3 -B tools/init_dev_env.py up -d
python3 -B tools/init_dev_env.py restart
python3 -B tools/init_dev_env.py down
```

Startup runs Rails database preparation and catalog synchronization. Review migrations before upgrades. Plain Compose does not bootstrap the host supervisor. Shutdown preserves `.dockerized-postgres/`, `ollama/`, agent resources and private MakeDocs recovery state; do not use prune, resets or manual state deletion as routine cleanup. Existing database initialization credentials are not rotated by editing `.env`.

The default stack is frontend, backend, PostgreSQL 18 and pinned Ollama. Default host ports 3099/3098/5499 bind to loopback; Ollama has no published host port. `/up` checks Rails and the required filesystem adapter, not semantic generation quality or full database/model readiness. Notes and annotations are installation-wide; there are no personal accounts.

## Project lifecycle

Register a relative reference such as `../example-project` in the frontend. It resolves from this library checkout on the host. Registration validates source identity and initializes metadata without inference; repeated equivalent registration is idempotent. Verified relocation requires matching identity, an absent previous source and no ambiguity. Removal preserves original source/manual documentation and archives eligible library content for recovery/re-registration.

Expected sequence: register → generate → update → remove registration → register again → generate again. An absent original `docs/` is supported; publication creates directories. UI and default CLI use `Documentation::Command`. Generation is mutating: only run it for a specifically authorized registered project, for example `docker compose exec -T backend make docs DOCS_ARGS='--project example-project'`. Pending delivery, ownership conflicts and recovery journals must be resolved through the documented flow, not deleted.

## Technical documentation

- [Architecture, integration and source map](docs/engineering-library/en/architecture/current-implementation.md)
- [Architecture decisions and current limits](docs/engineering-library/en/architecture/decisions.md)
- [Development, Docker and operational commands](docs/engineering-library/en/guides/application-development.md)
- [Host filesystem, publication and recovery](docs/engineering-library/en/operations/runtime-and-recovery.md)
- [Environment variables and configuration](docs/engineering-library/en/env/index.md)
- [MakeDocs, agent resources and evaluation](docs/engineering-library/en/training/local-documentation-command.md)
- [Technical FAQ](docs/engineering-library/en/faq/index.md)
- [Reader and approved source references](docs/engineering-library/en/guides/book-frontend.md)

Current source review: 2026-11-26, implementation baseline `246f58be`. Dated audits and validation reports remain historical evidence. This documentation consolidation did not execute generation, training, database preparation or a new lifecycle acceptance test. The private repository identity and existing agent/recovery artifacts are preserved.
