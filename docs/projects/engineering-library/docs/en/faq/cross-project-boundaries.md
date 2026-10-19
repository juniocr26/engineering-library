# Cross-project engineering questions

[Technical FAQ](index.md) · [Português brasileiro](../../pt-BR/faq/cross-project-boundaries.md)

Re-evaluated on 2026-10-19 from the historical `foundations.md` at `5052a8515b30278abea5fb81b37647482c10ba18` and selected current source. The six stable IDs below belong to this document. These are comparisons of independent portfolio projects, not an integrated platform or personal employment claims. Historical worker-absence statements are superseded; no application tests were executed here.

### Q001 — How do atomicity, durability and idempotence differ?

**Answer:** Each guarantee needs a boundary and failure model. ENV Auditor replaces one file atomically, without a workspace transaction or directory fsync. URL Shortener's Redis INCR is atomic at Redis, but does not commit a Cassandra mapping in the same transaction. The current relay producer couples its fact and outbox in PostgreSQL; the consumer couples receipt and stock, while broker confirms and ACKs remain external. Repeated transport and one supported local business effect can coexist because the consumer retains a deduplication receipt. Storage persistence and these SQL transactions do not by themselves prove power-loss recovery, backups or exactly-once delivery across systems.

Follow-up: Does timeout mean rollback? No. A remote write or COMMIT may have succeeded before its response was lost. Retry policy must preserve identity and reconcile possible effects instead of assuming no effect occurred.

### Q002 — What does a layered architecture actually protect?

**Answer:** Layers localize responsibilities when dependencies follow the intended contract. Go separates HTTP handlers, use cases and codecs through focused interfaces. Payment Lab maps entities to explicit DTOs inside its transaction, but depends on a concrete JPA repository. URL Shortener's service also imports concrete adapters, and encoding helpers still use global settings. Rust separates persistence/application contracts from SQLx and broker details. Engineering Library separates database catalog metadata from filesystem document content and browser layout. These are different degrees and purposes of separation, not interchangeable evidence of strict dependency inversion.

Follow-up: When introduce a port? When a concrete use case needs protocol independence, alternate adapters or meaningful controlled tests. A generic CRUD abstraction can obscure important operations such as acquiring ownership or reconciling uncertainty.

### Q003 — How can you reason about performance without inventing benchmarks?

**Answer:** Trace work, allocation and blocking, then label conclusions as analysis. ENV Auditor sorts discovery entries and can use quadratic membership work when appending many missing keys. Go buffers encoded and decoded data and uses native codecs; pixel limits do not establish total RSS. Payment Lab materializes an unpaginated visible-product list. URL Shortener performs synchronous store calls and central ID allocation. Engineering Library uses fixed-size database pagination but parses and measures document content separately. These identify measurement targets, not throughput or comparative language results.

Follow-up: What must a measurement report name? Input sizes/distributions, topology, versions, hardware, concurrency, warmup, units, method, correctness observations and limitations. No capacity measurement was run in this audit.

### Q004 — Which security mechanisms solve different problems?

**Answer:** Validation checks representation/invariants; authentication establishes identity; authorization permits actions; encryption protects confidentiality. URL syntax does not prevent abusive destinations, Basic requires protected transport, and reversible affine obfuscation is not encryption. Payment Lab's CORS policy controls browser behavior while explicit security rules deny unavailable routes. Engineering Library's signed cookie and reader-bound CSRF token isolate anonymous bookmark mutations, without providing private-document access control. ENV Auditor backup permissions reduce ordinary access while leaving plaintext. Go's pixel limits reduce selected resource risks without sandboxing native code.

Follow-up: Does a generic client error prove safe logs? No. The payment exception handler logs the original exception. Review each output/storage boundary separately; no secret values were inspected or published here.

### Q005 — What do fakes, integration tests and liveness establish?

**Answer:** Evidence concerns the assertions and fixtures actually exercised. Fakes can check call ordering and HTTP/error translation while excluding real stores or codecs. Testcontainers PostgreSQL tests can check migrations and selected constraints in isolated databases, without proving restoration of an existing volume. A health endpoint may establish serving/boot only; the payment readiness group explicitly includes the database, while Rails `/up` does not query catalog data. A checked-in test definition or historical green result is not a newly executed test.

Follow-up: What should the next test target? A material unproven invariant at its failure boundary, such as unknown commit acknowledgement or stale ownership. Structural documentation checks establish links/navigation, not semantic truth, translation quality or actual browser layout.

### Q006 — How do rollback and recovery differ?

**Answer:** Artifact rollback switches code; recovery establishes valid data and operational state. Go must retain compatible native codecs/builds. ENV Auditor recovery needs the correct exact-original backup and awareness of later edits. URL Shortener must keep counter state, mappings and public-code configuration coherent. Payment Lab must preserve Flyway history and initialized database identity. The relay must preserve event/receipt history and reconcile uncertain delivery; its worker and consumer now exist. Library bookmarks depend on logical paths/anchors and browser identity as well as PostgreSQL rows.

Follow-up: Is a down migration a backup? No. It can remove schema/data or fail when old constraints no longer hold. For example, the relay's new multiple-action down migration tries to restore unique run ownership and refuses when several retained actions exist; discarding evidence to force it would change the recovery problem. No production restore drill, RTO or RPO was measured here.
