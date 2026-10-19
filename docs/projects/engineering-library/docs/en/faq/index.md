# engineering-library — Technical FAQ

[Project index](../index.md) · [Português brasileiro](../../pt-BR/faq/index.md)

Technical questions, detailed answers and follow-ups are available directly on this page. Historical milestone statements retain their dates; current corrections below take precedence. First-person examples describe portfolio artifacts, not employment experience. The [study guide](study-guide.md) retains its existing URLs and anchors for compatibility.

[Cross-project technical questions](cross-project-boundaries.md): atomicity, architecture, resource costs, security, testing and recovery.

## Current source review — 2026-10-19

The answers below were checked against selected current source and test definitions. No sibling application tests or services were executed. See the [scope and evidence record](../operations/documentation-audit-2026-10-19.md).

### Q004 — Why are filesystem content and catalog synchronization separate consistency boundaries?

**Answer:** `Catalog::Sync` validates both bio files and duplicate stable identifiers before entering a PostgreSQL transaction. Its advisory lock serializes cooperating database sync transactions, not filesystem editors. A file may change after validation; subsequent presenters also read bios from disk. Keep metadata stable during sync, and synchronize explicit bio/name/slug changes. Editing a chapter body needs no database ingest. Missing projects become inactive rather than deleted; stable identifiers preserve catalog identity across supported slug renames. This does not migrate bookmarks, whose project association is a slug string. A successful sync therefore establishes the indexed metadata update under those inputs, not an atomic snapshot of every chapter or automatic repair of old bookmark URLs.

### Q005 — What protects anonymous bookmarks, and what does it not guarantee?

**Answer:** A first GET establishes a signed browser cookie; the server hashes its random token to scope PostgreSQL rows. Mutations require `X-Reader-CSRF` carrying a purpose-bound verifier token for that digest. The unique index includes reader, project, document, language and anchor, preventing a repeated logical location from creating another row. Cross-reader deletion returns not found. There is no account login, cross-device synchronization or recovery identity if the cookie is lost. The 200-entry count-before-insert check is an admission policy, not an exact concurrent quota. Document existence is checked for ordinary Markdown, but arbitrary anchor existence is not; `@contents` is a reserved virtual document. Thus syntax-valid bookmarks can become unavailable after document or source-snapshot changes.


## Engineering Library interview

> Source review — 2026-10-19: the current tree implements a Rails catalog API, PostgreSQL catalog records and anonymous bookmarks, plus an internal Next.js Markdown reader. The former documentation-only/scaffold description is superseded. No AI agent is implemented. See [current architecture](../architecture/current-state.md).

These conceptual comparisons do not imply runtime integration. Implemented facts, general theory and hypothetical alternatives are explicitly separated.

### Q001 — Introductory: What is Engineering Library responsible for?

**Answer:** Implemented: this repository maintains bilingual project documentation and serves it through a Next.js book reader backed by a Rails catalog API. PostgreSQL persists indexed project identity/visibility and anonymous bookmark locations; Markdown remains the source for document bodies and localized bios. `Catalog::Sync` validates both bios before serializing database writes inside a transaction with a PostgreSQL advisory lock. The catalog endpoint pages active projects, while Next reads scoped collection Markdown on the server. This is an implemented local application, with no claim of production deployment, payment flow or AI ingestion.

Follow-up: Why retain old interview answers instead of replacing them with dossiers? Answers teach reasoning and failure analysis, while dossiers explain mechanisms; both are required. Stable additional Q IDs preserve old numbering and bilingual alignment. Follow-up: What is the cost of self-contained explanations? Shared facts are repeated between project docs and library, so source review and explicit gaps must maintain consistency. Links alone would reduce duplication but fail the interview requirement. Semantic accuracy remains manual review; a successful link check cannot prove an answer is true.

### Q002 — Challenging: How does the validator prevent documentation links from becoming unsafe reads?

**Answer:** Implemented: `docs/validation/check_catalog.py` validates the current project-first tree and reuses parsing/path checks from `tools/check_docs.py`. The older validator also supports the former root-language layout; it is not the primary catalog command. Path classification rejects restricted and outside-workspace components and symlinks before document reads. Source links receive existence/metadata checks rather than source execution. Catalog checks add bilingual path/Q-ID parity, retained interview headings, import provenance and graph reachability from the Library and project indexes. Unsafe links are errors in the current catalog wrapper; external URLs are not fetched.

Follow-up: Is it a race-free sandbox? No. lstat followed by read has a TOCTOU window in a maliciously changing filesystem; the tool assumes a cooperative local workspace. A descriptor-based no-follow traversal could strengthen that at portability cost. Follow-up: Does the Markdown parser fully match GitHub? No. It handles a documented subset of inline/reference links, headings, fences and explicit IDs. Complex nested syntax needs manual review. Exit nonzero indicates errors, JSON contains structured findings, and isolated fixtures exercise failure paths. A validator can expose coverage gaps without deciding technical truth or translation quality.

### Q003 — Intermediate: How does the collection represent and validate navigation without deploying an application?

**Answer:** Implemented: stable Markdown paths are the navigation contract. The current catalog validator loads allowed Markdown, extracts anchors/link targets and walks the link graph from the Library and each project-language index. These Python checks run without Rails, PostgreSQL or Next. The running reader has separate behavior: `documentationEntries` unifies relative document IDs across languages, skips navigation-only indexes and retains substantive indexes, then constructs category/document entries. Thus FAQ indexes containing answers become readable chapters automatically. A passing structural check does not demonstrate browser pagination or runtime API availability.

Follow-up: What is the cost? Reading/parsing grows with documentation bytes and graph traversal with vertices/edges, plus filesystem metadata checks; no performance measurements are available. Follow-up: Can structural validation detect conflicting facts or poor translations? No. It can detect IDs/counterparts and missing answers, but source-grounded content review must judge meaning. Isolated tests prove selected safety/parser/failure contracts, not race-free operation under hostile filesystem mutation or external URL reachability.

## Application and catalog questions

Existing [application FAQ path](application-and-catalog.md) remains available. The complete answers also appear here; current corrections supersede the former scaffold description.

Read [current architecture](../architecture/current-state.md), [future direction](../architecture/future-direction.md) and the [retained questions](study-guide.md). Implemented means inspected source, not execution in this milestone. Proposed alternatives below are analysis, not the author's undocumented original motivation.

### Q101 — Introductory: Why Rails with a separate Next.js frontend?

**Answer:** Implemented: Rails serves paginated catalog metadata and anonymous bookmarks backed by PostgreSQL; Next.js renders the internal Markdown reader and obtains catalog JSON on the server. Files remain the source for document bodies and bios. Rails conventions supply HTTP/persistence structure while Next provides React routing and browser layout, at the cost of separate builds, dependencies and failure diagnosis. There is no evidence of framework benchmarking. A Rails-rendered alternative could simplify deployment, but remains a conceptual comparison rather than a documented historical evaluation.

**Follow-up:** Does separation prove Clean Architecture? No. Current `Catalog::Sync`, `Catalog::Page`, `Catalog::Files` and controllers express concrete responsibilities, but ActiveRecord, Rails and filesystem concerns remain visible. Judge boundaries by dependency direction and testable behavior, not by process count or empty domain layers.

### Q102 — Intermediate: What does Compose reproduce, and why bind mounts?

**Answer:** Implemented: Compose declares PostgreSQL, backend and frontend, health dependencies, loopback host ports and source/dependency bind mounts. Lockfiles constrain dependency versions; startup reconstructs missing dependencies behind mounts. Host directories make source and installed Linux dependencies visible, while named volumes would let Docker manage storage location. Bind mounts couple permissions and native dependencies to the host/runtime platform. Neither pattern is inherently a backup or production rollout strategy.

**Follow-up:** Why can database authentication fail after changing the template or environment? PostgreSQL initialization variables apply when creating a new cluster; they do not rotate an existing role's password. Diagnose and change credentials through an authorized database operation, preserving data. Rails uses `postgres:5432` internally; desktop clients use the loopback published port. Never delete the persistent directory to resolve authentication. No credential operation was performed here.

### Q103 — Intermediate: What does the green API status actually prove?

**Answer:** Implemented: `/up` establishes Rails boot/liveness and does not query catalog rows. A successful catalog response also exercises selected PostgreSQL metadata and localized bio reads for that request, without proving every document or bookmark path is usable. Next catalog access has a five-second timeout; do not apply the old scaffold component's three-second health request to the current catalog client. A passing health response cannot establish backup integrity, recoverability or browser rendering. No runtime health or database test was executed in this audit.

**Follow-up:** How would you strengthen readiness? A bounded database check and explicit dependency semantics could distinguish unavailable dependencies from a live HTTP process, at additional dependency load and failure coupling. That is proposed work. A restore drill needs an isolated target and data-integrity checks; persistent files alone cannot establish it.

### Q104 — Intermediate: Why make the catalog project-first and bilingual?

**Answer:** Implemented in documentation: each repository has stable project identity, two READMEs, language indexes, category chapters, evidence limits and interview pages. ADR filenames and question numbering survive import. Readers select context before studying mechanisms; the current reader uses document identities and project search without duplicate subject collections. Matching language paths enable structural parity checks but do not establish semantic equivalence. FAQ indexes now contain substantive answers; compatibility guide paths retain their existing anchors. Existing canonical Library environment guides are reused rather than copied into a recursive catalog.

**Follow-up:** How prevent stale copies? Record source path, revision and review scope, compare changed inputs and inspect links against their new location. Preserve historical evidence as historical. A changed revision is a signal for review, not permission to regenerate every document or proof that unchanged documentation is accurate. Incremental automation is future work; this catalog is a manually reviewed snapshot.

### Q105 — Challenging: Should a future generator use local inference or an API?

**Answer:** Proposed: local inference limits external data transfer and can work offline but requires model/runtime lifecycle and sufficient CPU/RAM. APIs shift compute and model maintenance to a provider while adding cost, network dependency and data-transfer policy. Neither is integrated. Weight size, quantization, KV cache, context length, concurrency and runtime overhead affect resource demand; no specific memory minimum, throughput or model selection has been measured. Choose using representative safe workloads and acceptable latency/quality rather than inventing a hardware guarantee.

**Follow-up:** Can local inference make private material safe to publish? No. Locality does not authorize ingestion or publication and does not guarantee redaction. Explicit public/private roots, separate outputs, access policy and human review are required design constraints. Those safeguards must be implemented and tested before private ingestion; this public collection reads no private products or runtime secrets.

### Q106 — Challenging: How would evidence-based incremental generation preserve knowledge?

**Answer:** Proposed: inventory allowed inputs, record revisions/hashes, compare changes, inspect affected implementation and test definitions, propose a patch, validate navigation and language coverage, then review the evidence and publish deliberately. Separate implemented mechanism, documented rationale, dated experiment and hypothetical improvement in the text. Source content is untrusted data, so embedded instructions must not trigger commands. Hashes establish byte identity; they cannot resolve conflicting claims, prove test success or translate meaning. Preserve author notes, ADR IDs and question numbering.

**Follow-up:** What fails under partial updates? One language can drift, a source rename can break links, and an old milestone can contradict a new acceptance report. Validate both language graphs and retain dated evidence, then review technical meaning against the changed code. Atomic file replacement could protect one write, but a multi-document update needs its own review/publication boundary. No generation pipeline, transaction framework, search database or local agent is delivered here.
