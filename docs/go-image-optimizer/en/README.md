# go-image-optimizer

[English](README.md) | [Português brasileiro](../pt-br/README.md)

A Go and Next.js application for synchronous image compression, resizing, format conversion and browser preview fallback. Processing is request-scoped, with no database or persistent upload storage.

## Documentation catalog and reading path

- [Complete categorized catalog](index.md)
- [Review checklist and evidence gaps](operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [001 native image codecs](adr/001-native-image-codecs.md)
- [Architecture](architecture/overview.md)
- [Development dependencies and recovery](docker/development.md)
- [Docker and configuration](docker/runtime.md)
- [Project guide](guides/project-guide.md)
- [Testing](testing/strategy.md)
- [Validation results](testing/verification.md)

[License](../../../../../Portifo%CC%81lio/go-image-optimizer/LICENSE)

## Quick start and scope

Install Docker with Compose v2, then run from this repository:

```sh
docker compose up --build backend frontend
```

UI: http://localhost:3000; API: http://localhost:8080. Native codecs are built by the Dockerfiles. There is no database or persistent upload history.

[Installation, execution flow, operational limits and project interview](guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.
