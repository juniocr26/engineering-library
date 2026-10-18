# Engineering Library

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
# First setup / primeira configuração
docker compose exec backend bin/rails db:prepare catalog:sync
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
