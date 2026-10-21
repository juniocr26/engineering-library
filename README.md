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

## Local dependency sources (Docker development)

The existing `frontend` and `backend` services install dependencies through their entrypoints at startup. `npm ci --include=dev` populates physical `frontend/node_modules` (container `/app/frontend/node_modules`); frozen `bundle install` populates `backend/vendor/bundle/ruby/3.4.0/` (the current Ruby ABI) (container `/app/backend/vendor/bundle`). These paths are part of the existing source bind mounts, with no nested dependency volume or tmpfs. Image-layer packages remain separate; development installs do not depend on files hidden by source mounts. Startup needs registry access when packages are unavailable locally; npm replaces its dependency tree on every startup, while Bundler reuses installed locked gems. The npm cache is container-local under `/tmp`, so recreation generally needs registry access.

From the repository root, after preparing `.env`:

```sh
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 600
# Refresh dependencies after changing lockfiles, without racing live processes:
docker compose stop frontend backend
docker compose up -d --wait --wait-timeout 600 backend frontend
# Recreate only application containers; preserve PostgreSQL and its data:
docker compose up -d --force-recreate --no-deps --wait --wait-timeout 600 backend frontend
# Inspect resolution inside the existing running services:
docker compose exec -T frontend node -p 'require.resolve("next/package.json")'
docker compose exec -T backend bundle check
docker compose exec -T backend bundle show rails
```

No host Node.js, npm, Ruby or Bundler is required. Keep the directories writable by the configured `LOCAL_UID`/`LOCAL_GID` (default 1000:1000 on Docker Desktop); installs run as this user, without recursive permission changes. Generated contents are already ignored by Git and Docker contexts; preserve tracked `backend/vendor/.keep`. `.next`, Rails logs and temporary files remain ephemeral. Never delete database data or use `docker compose down -v` to refresh dependencies. Dependency image targets and their installation paths are unchanged; these entrypoints and Compose mounts are for development.

VS Code can read local package sources, TypeScript declarations and Ruby gem sources. The checked `frontend/tsconfig.json` uses bundler module resolution, the Next plugin and the `@/*` alias; no additional alias to container paths is needed. Its `.next` generated type directories remain container-only tmpfs, so those declarations are not available locally. The ignored `.vscode/settings.json` inspected here contains only color settings. The local VS Code installation has built-in TypeScript support; no Ruby language extension was found in its local extensions directory. This is not a live diagnostics check. Physical gems alone do not provide Ruby IntelliSense: Ruby LSP needs an extension, a compatible Ruby and a language-server process ([VS Code Ruby documentation](https://code.visualstudio.com/docs/languages/ruby)). No runtime, extension or remote editor architecture was installed; ask for approval before introducing such an approach. ESLint extension execution is also not validated. Linux native modules and gems are for container execution, not macOS execution. Application commands and checks remain in Docker.
