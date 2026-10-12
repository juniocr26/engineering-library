# Engineering Library

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
