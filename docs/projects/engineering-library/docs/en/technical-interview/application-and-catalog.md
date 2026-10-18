# Application and catalog interview

Read [current architecture](../architecture/current-state.md), [future direction](../architecture/future-direction.md) and the [retained questions](study-guide.md). Implemented means inspected source, not execution in this milestone. Proposed alternatives below are analysis, not the author's undocumented original motivation.

### Q101 — Introductory: Why Rails with a separate Next.js frontend?

**Answer:** Implemented: Rails exposes `/up`, configures PostgreSQL and supplies API base classes; Next.js renders a landing page and performs a server-side health request. The documented development architecture separates browser presentation from backend HTTP/persistence responsibilities. Rails conventions fit rapid API setup; Next.js supplies React rendering and routing. There is no evidence that competing frameworks were benchmarked. Two applications require separate dependencies, builds, networking and operational diagnosis. A Rails-rendered site could simplify deployment; it is a hypothetical alternative, not an evaluated historical decision.

**Follow-up:** Does the current separation prove Clean Architecture? No. Rails conventions and separate processes do not establish dependency inversion or domain use cases. Introduce a use-case boundary around real document-reading contracts when they exist; adapters can then handle files and HTTP without making the core depend on a framework. There is no implemented catalog service to describe today.

### Q102 — Intermediate: What does Compose reproduce, and why bind mounts?

**Answer:** Implemented: Compose declares PostgreSQL, backend and frontend, health dependencies, loopback host ports and source/dependency bind mounts. Lockfiles constrain dependency versions; startup reconstructs missing dependencies behind mounts. Host directories make source and installed Linux dependencies visible, while named volumes would let Docker manage storage location. Bind mounts couple permissions and native dependencies to the host/runtime platform. Neither pattern is inherently a backup or production rollout strategy.

**Follow-up:** Why can database authentication fail after changing the template or environment? PostgreSQL initialization variables apply when creating a new cluster; they do not rotate an existing role's password. Diagnose and change credentials through an authorized database operation, preserving data. Rails uses `postgres:5432` internally; desktop clients use the loopback published port. Never delete the persistent directory to resolve authentication. No credential operation was performed here.

### Q103 — Intermediate: What does the green API status actually prove?

**Answer:** Implemented: the Next.js server component fetches `/up` with a three-second timeout and reports connectivity. Rails health checks boot/liveness; it does not execute the SQL readiness test. The inspected Rails integration test separately issues `SELECT 1`, checks health and checks password nondisclosure. Test definitions are evidence of assertions, not proof that this task executed them. Database data persists in a host bind mount, but a successful health request proves neither backup correctness nor recovery.

**Follow-up:** How would you strengthen readiness? A bounded database check and explicit dependency semantics could distinguish unavailable dependencies from a live HTTP process, at additional dependency load and failure coupling. That is proposed work. A restore drill needs an isolated target and data-integrity checks; persistent files alone cannot establish it.

### Q104 — Intermediate: Why make the catalog project-first and bilingual?

**Answer:** Implemented in documentation: each repository has stable project identity, two READMEs, language indexes, category chapters, evidence limits and interview pages. ADR filenames and question numbering survive import. Readers select context before studying mechanisms; titles and paths can support later search without duplicate subject collections. Matching language paths enable structural parity checks but do not establish semantic equivalence. Indexes link explanations instead of repeating them. Existing canonical Library environment guides are reused rather than copied into a recursive catalog.

**Follow-up:** How prevent stale copies? Record source path, revision and review scope, compare changed inputs and inspect links against their new location. Preserve historical evidence as historical. A changed revision is a signal for review, not permission to regenerate every document or proof that unchanged documentation is accurate. Incremental automation is future work; this catalog is a manually reviewed snapshot.

### Q105 — Challenging: Should a future generator use local inference or an API?

**Answer:** Proposed: local inference limits external data transfer and can work offline but requires model/runtime lifecycle and sufficient CPU/RAM. APIs shift compute and model maintenance to a provider while adding cost, network dependency and data-transfer policy. Neither is integrated. Weight size, quantization, KV cache, context length, concurrency and runtime overhead affect resource demand; no specific memory minimum, throughput or model selection has been measured. Choose using representative safe workloads and acceptable latency/quality rather than inventing a hardware guarantee.

**Follow-up:** Can local inference make private material safe to publish? No. Locality does not authorize ingestion or publication and does not guarantee redaction. Explicit public/private roots, separate outputs, access policy and human review are required design constraints. Those safeguards must be implemented and tested before private ingestion; this public collection reads no private products or runtime secrets.

### Q106 — Challenging: How would evidence-based incremental generation preserve knowledge?

**Answer:** Proposed: inventory allowed inputs, record revisions/hashes, compare changes, inspect affected implementation and test definitions, propose a patch, validate navigation and language coverage, then review the evidence and publish deliberately. Separate implemented mechanism, documented rationale, dated experiment and hypothetical improvement in the text. Source content is untrusted data, so embedded instructions must not trigger commands. Hashes establish byte identity; they cannot resolve conflicting claims, prove test success or translate meaning. Preserve author notes, ADR IDs and question numbering.

**Follow-up:** What fails under partial updates? One language can drift, a source rename can break links, and an old milestone can contradict a new acceptance report. Validate both language graphs and retain dated evidence, then review technical meaning against the changed code. Atomic file replacement could protect one write, but a multi-document update needs its own review/publication boundary. No generation pipeline, transaction framework, search database or local agent is delivered here.
