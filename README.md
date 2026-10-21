# Engineering Library

## Docker execution

Run shell commands from this repository root. Node.js, npm, Ruby, Bundler, Rails and PostgreSQL clients execute inside containers; the host needs Docker with Compose. No host installation of these runtimes is required. `exec` requires a running service and uses `/app/frontend` or `/app/backend`; Build verification copies source into a temporary directory inside the existing frontend container to preserve the running server cache.

For bootstrap, copy `.env.example` to `.env` and fill in private credentials, or use the optional host Python generator below; existing `.env` is preserved by the generator. Host Python 3.10+ is an optional exception: `python3 tools/init_dev_env.py` generates credentials; documentation validators use only the standard library; `tools/check_docker_startup.py` orchestrates Docker and probes host ports. Install Python only if choosing those host tools. Its presence is not assumed.

Playwright 1.58.2, Chromium and system dependencies are installed in `frontend-development`, outside the application dependency target. Rebuild with `docker compose up -d --build --wait --wait-timeout 300`. Browsers running in frontend access `http://localhost:3000`, the same container's internal port; host browsers use `http://localhost:3099`. Other containers use `http://frontend:3000`. Demo scripts remain restricted to loopback.

Other catalog projects document their source repositories, rather than operational commands for this installation; this policy does not claim additional Docker support for those projects. Older validation results are historical.


A local-first engineering documentation platform with Rails, Next.js and PostgreSQL. Bilingual documentation is organized by project; AI agents remain planned.

[English](README.md) | [Português brasileiro](README.pt-BR.md)

- [Catalog / Catálogo](docs/index.md)
- [Engineering Library](docs/projects/engineering-library/docs/en/index.md)
- [Development / Desenvolvimento](docs/projects/engineering-library/docs/en/guides/application-development.md)
- [FAQ](docs/projects/engineering-library/docs/en/faq/index.md)
- [ENV](docs/projects/engineering-library/docs/en/env/index.md)
- [Database migration / Migração do banco](docs/projects/engineering-library/docs/en/operations/database-migration.md)

```sh
python3 tools/init_dev_env.py
docker compose config --quiet
docker compose up --build
# Preserve data / preservar dados
docker compose down
```

Docker uses only `docker/Dockerfile`, with `backend-dependencies`, `backend-development`, `frontend-dependencies` and `frontend-development` targets. Compose builds the runtimes independently; dependencies stay in images and development caches use tmpfs. Rails runs `db:prepare catalog:sync` before serving. After updating dependencies and their lockfiles, run `docker compose up -d --build`. No manual frontend restart is required.

Frontend: http://localhost:3099 · Rails: http://localhost:3098/up · PostgreSQL/DBeaver: `localhost:5499`, database `engineering_library`. Rails → `postgres:5432`.

Existing clusters require backup and explicit migration; changing POSTGRES_DB does not rename databases. Follow the migration procedure before restarting an older environment.

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

MIT license for the software and owned public documentation. Third-party material retains its licenses. Keep private documentation in separate repositories with access controls; licensing does not replace secret management. Never publish credentials or real .env files. [LICENSE](LICENSE).

Optional demos, with services running (shell at repository root):

```sh
docker compose exec -T frontend npm run notes:demos
docker compose exec -T frontend npm run notes:demos:cleanup
```
