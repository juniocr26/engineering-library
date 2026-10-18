# go-image-optimizer

[English](README.md) | [Português brasileiro](README.pt-BR.md)

A Go and Next.js application for synchronous image compression, resizing, format conversion and browser preview fallback. Processing is request-scoped, with no database or persistent upload storage.

## Documentation catalog and reading path

- [Complete categorized catalog](docs/en/index.md)
- [Review checklist and evidence gaps](docs/en/operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [001 native image codecs](docs/en/adr/001-native-image-codecs.md)
- [Architecture](docs/en/architecture/overview.md)
- [Development dependencies and recovery](docs/en/docker/development.md)
- [Docker and configuration](docs/en/docker/runtime.md)
- [Project guide](docs/en/guides/project-guide.md)
- [Testing](docs/en/testing/strategy.md)
- [Validation results](docs/en/testing/verification.md)

[License](../../../../go-image-optimizer/LICENSE)

## Quick start and scope

Install Docker with Compose v2, then run from this repository:

```sh
docker compose up --build backend frontend
```

UI: http://localhost:3000; API: http://localhost:8080. Native codecs are built by the Dockerfiles. There is no database or persistent upload history.

[Installation, execution flow, operational limits and project interview](docs/en/guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.

<!-- collection entry -->
## Engineering Library collection

[Library](../../index.md) | [English](docs/en/index.md) | [Português brasileiro](docs/pt-BR/index.md) | [Interview](docs/en/faq/index.md) | [Provenance](docs/en/operations/source-review.md)

Go/Next.js synchronous image compression, resize, conversion and preview with native codecs.

[Project bio](bio/en.md)
