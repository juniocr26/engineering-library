# Engineering Library

A local-first engineering documentation platform, now with a Docker-based Rails API, Next.js frontend and PostgreSQL foundation. The existing bilingual reference collection remains available. [Application setup and architecture](docs/en/guides/application-development.md).

[English](README.md) | [Português brasileiro](README.pt-BR.md)

A self-contained bilingual technical reference and interview-preparation collection for ENV Auditor, Go Image Optimizer, URL Shortener, Rust Event Relay and Payment Reconciliation Lab. The guides explain implemented behavior, alternatives and limitations; suggested answers should be adapted to experience you can demonstrate.

## Documentation catalog and reading path

- [Complete categorized catalog](docs/en/index.md)
- [Review checklist and evidence gaps](docs/en/operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

Interview preparation is a core responsibility: retain and rehearse substantive answers, including answered follow-ups and limits, in both languages. The collection also supplies complete project dossiers and conceptual foundations.

## Documentation

- [env auditor](docs/en/interviews/env-auditor.md)
- [go image optimizer](docs/en/interviews/go-image-optimizer.md)
- [Setup and execution](docs/en/guides/setup.md)
- [url shortener](docs/en/interviews/url-shortener.md)
- [Validation results](docs/en/testing/verification.md)
- [Rust Event Relay](docs/en/interviews/rust-event-relay.md)
- [Payment Reconciliation Lab](docs/en/interviews/payment-reconciliation-lab.md)

## Study order

Start with ENV Auditor for local discovery/parsing/failure boundaries, then Go Image Optimizer for HTTP, interfaces and resource lifetimes. Study URL Shortener next for two-store partial failures, encoding and consistency; use the retained Payment Reconciliation Lab catalog to compare DTO/JPA/security boundaries and distinguish a domain transition from delivered workflows. Finish with Rust Event Relay for durable state, broker uncertainty and ownership contracts. Each guide orders its own prerequisites and follow-up questions. These are suggested study steps, with no topics marked completed.

[Rust worker composition and operational lessons](docs/en/architecture/rust-event-relay.md).

[Rust recovery and reliability limits](docs/en/architecture/rust-event-relay.md).

## Current workspace and validation

Start with the [workspace catalog](docs/en/architecture/workspace-catalog.md), follow a project dossier into its interview answers, then compare foundations and verified flows. The Rust dossier covers the accepted final local producer/consumer/UI scope; older milestone reviews are historical. Run from the parent workspace:

```sh
python3 -B engineering-library/tools/check_docs.py --workspace .
python3 -B -m unittest discover -s engineering-library/tools -p test_check_docs.py -v
```

Only Python 3.10+ is required for local documentation validation; no application installation is required. [2026-10-18 review and remaining evidence gaps](docs/en/operations/workspace-review-2026-10-18.md).

## Application scaffold

Rails API + Next.js + PostgreSQL development foundation. Existing documentation is preserved below. AI features remain planned.

[Docker, architecture, versions, DBeaver, dependency recovery and tests](docs/en/guides/application-development.md).

```sh
python3 tools/init_dev_env.py
docker compose up --build
# another terminal / outro terminal
docker compose exec backend bin/rails db:prepare
# shutdown / encerrar
docker compose down
```
