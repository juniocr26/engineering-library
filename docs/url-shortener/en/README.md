# url-shortener

[English](README.md) | [Português brasileiro](../pt-br/README.md)

A FastAPI portfolio demonstrating authenticated URL creation and public permanent redirects. Redis allocates IDs; Cassandra stores mappings; Base62 and reversible obfuscation produce short codes. It explores system-design trade-offs without claiming measured production capacity.

## Documentation catalog and reading path

- [Complete categorized catalog](index.md)
- [Review checklist and evidence gaps](operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [Architecture](architecture/overview.md)
- [Development dependencies and recovery](docker/development.md)
- [Docker and configuration](docker/runtime.md)
- [Project guide](guides/project-guide.md)
- [Postman collection](api/postman.md)
- [Testing](testing/strategy.md)
- [Validation results](testing/verification.md)

[License](../../../../../Portifo%CC%81lio/url-shortener/LICENSE)

## Quick start and scope

For a fresh clone, install Docker/Compose, copy the example and privately configure Basic Auth, obfuscation and database credentials:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose build
docker compose up -d
```

API: http://localhost:8000. Startup includes three Cassandra nodes and role/schema bootstrap. POST /urls requires Basic Auth; GET /{short_code} is public. Coordinate counter and mapping recovery; there is no cross-store transaction.

For existing checkouts, update configuration deliberately instead of overwriting the local file.

[Installation, execution flow, operational limits and project interview](guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.
