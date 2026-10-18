# Workspace catalog and learning paths

2026-10-18. Six immediate Git repositories; all initially clean. No archived/reference repository was discovered at the parent level. Nested frontend/backend directories are components, not separate projects. Dependency caches, build outputs, test fixtures and audit evidence are not projects.

| Repository | Revision | Responsibility | Study |
| --- | --- | --- | --- |
| engineering-library | `0eb8085e4461` | Bilingual self-contained reference, interviews and read-only documentation validation. | [Collection interview](../interviews/engineering-library.md) |
| env-auditor | `000949ff926f` | Literal local environment-key synchronization; ordered blocks, plans and per-file replacement. | [Dossier](env-auditor.md) / [Q&A](../interviews/env-auditor.md) |
| go-image-optimizer | `2c9a27f40a2a` | Synchronous Go image processing with Next.js proxy and native codecs; no durable jobs. | [Dossier](go-image-optimizer.md) / [Q&A](../interviews/go-image-optimizer.md) |
| payment-reconciliation-lab | `71b8b8f22d38` | Retained read-only catalog; Spring/JPA/Flyway and Angular. Reconciliation/Stripe remain planned. | [Dossier](payment-reconciliation-lab.md) / [Q&A](../interviews/payment-reconciliation-lab.md) |
| rust-event-relay | `6e5e64fbffea` | Final accepted local producer/outbox/AMQP/consumer/UI scope, with bounded real scenarios and explicit simulations. | [Dossier](rust-event-relay.md) / [Q&A](../interviews/rust-event-relay.md) |
| url-shortener | `40e4ea05d6e4` | FastAPI creation/301 resolution; Redis IDs and Cassandra mappings; no joint transaction. | [Dossier](url-shortener.md) / [Q&A](../interviews/url-shortener.md) |

## Reading paths

Run a project: open its own README and setup; sibling repositories are optional references. Understand architecture: read the dossier, then trace the named records/calls. Test/troubleshoot: use that project’s strategy and operations, distinguishing historical execution from current instructions. Interview: rehearse purpose, mechanism, failure window, alternative and evidence limit.

Recommended order: ENV Auditor (representation/filesystem), Go (HTTP/resources), URL Shortener (two-store failures), Payment Lab (DTO/SQL/domain transition), Rust (durable authority, uncertainty and effects), then [foundations](../interviews/foundations.md). [Verified relationships](../integrations/verified-flows.md) and [completion/evidence review](../operations/workspace-review-2026-10-18.md) explain the scope. No application depends on Engineering Library.
