# Workspace catalog and learning paths

This parent workspace contains six independent Git repositories. Static code inspection on 2026-10-10 found no runtime integration from one portfolio application to another. Shared use of Docker, HTTP, Python or PostgreSQL is conceptual overlap, not an ecosystem call graph. ENV Auditor can scan sibling directories as filesystem inputs; that is not a network client of these applications. Engineering Library is a documentation/tooling collection, not an application dependency.

| Repository | Current responsibility | Main representation / boundary | Start here |
| --- | --- | --- | --- |
| env-auditor | Literal environment-key synchronization | Ordered blocks, local files, per-file replacement | [Dossier](env-auditor.md), [interview](../interviews/env-auditor.md) |
| go-image-optimizer | Synchronous compression/resize/conversion/preview | Multipart, pixels, native codecs, browser blobs | [Dossier](go-image-optimizer.md), [interview](../interviews/go-image-optimizer.md) |
| url-shortener | Authenticated creation, public 301 resolution | Redis ID, affine Base62 code, Cassandra mapping | [Dossier](url-shortener.md), [interview](../interviews/url-shortener.md) |
| payment-reconciliation-lab | Retained read-only catalog during domain transition | JPA entities, DTOs, constrained PostgreSQL schema | [Dossier](payment-reconciliation-lab.md), [interview](../interviews/payment-reconciliation-lab.md) |
| rust-event-relay | HTTP liveness plus separately callable reader/publisher/ownership models | Envelope, snapshot, confirmed publish, future authority ports | [Dossier](rust-event-relay.md), [interview](../interviews/rust-event-relay.md) |
| engineering-library | Self-contained explanations and interview preparation | Bilingual Markdown and read-only validator | [Collection interview](../interviews/engineering-library.md), [validator](../guides/documentation-validator.md) |

For a first pass, trace ENV Auditor's parse/plan/write boundary, then Go's HTTP/pixel boundary, URL Shortener's two-store failure boundary, Payment Lab's DTO/transaction boundary and Rust's snapshot/authority/broker boundary. For a deeper pass, rehearse an introductory explanation, defend the mechanism with source evidence, then answer a failure-window question and compare one alternative. The [cross-cutting interview](../interviews/foundations.md) supplies concepts; [verified flows](../integrations/verified-flows.md) explains actual paths end to end. Nothing here marks a learner as having completed study.

Recorded runtime checks remain historical. This review ran only documentation validation and isolated validator tests. No applications, containers, migrations, benchmarks, network requests or deployment were executed. [Completion report](../operations/workspace-completion.md) records every repository and its remaining evidence gaps.
