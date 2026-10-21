# Engineering Library

## Docker execution

Run shell commands from this repository root. Node.js, npm, Ruby, Bundler, Rails and PostgreSQL clients execute inside containers; the host needs Docker with Compose. No host installation of these runtimes is required. `exec` requires a running service and uses `/app/frontend` or `/app/backend`; Build verification copies source into a temporary directory inside the existing frontend container to preserve the running server cache.

For bootstrap, copy `.env.example` to `.env` and fill in private credentials, or use the optional host Python generator below; existing `.env` is preserved by the generator. Host Python 3.10+ is an optional exception: `python3 tools/init_dev_env.py` generates credentials; documentation validators use only the standard library; `tools/check_docker_startup.py` orchestrates Docker and probes host ports. Install Python only if choosing those host tools. Its presence is not assumed.

Playwright 1.58.2, Chromium and system dependencies are installed in `frontend-development`, outside the application dependency target. Rebuild with `docker compose up -d --build --wait --wait-timeout 300`. Browsers running in frontend access `http://localhost:3000`, the same container's internal port; host browsers use `http://localhost:3099`. Other containers use `http://frontend:3000`. Demo scripts remain restricted to loopback.

Other catalog projects document their source repositories, rather than operational commands for this installation; this policy does not claim additional Docker support for those projects. Older validation results are historical.


<!-- collection entry -->
## Engineering Library collection

[Library](../../index.md) | [English](docs/en/index.md) | [Português brasileiro](docs/pt-BR/index.md) | [Interview](docs/en/faq/index.md) | [Provenance](docs/en/operations/source-review.md)

Bilingual engineering knowledge and interview library with a Rails/Next.js/PostgreSQL development scaffold. Includes a book-themed bilingual frontend and a PostgreSQL-backed catalog API; the internal Markdown reader supports measured pagination, search, chapters and shared PostgreSQL bookmarks.

[Project bio](bio/en.md)
