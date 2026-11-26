# engineering-library — Technical FAQ

[Project index](../index.md) · [Português brasileiro](../../pt-br/faq/index.md)

Technical questions, detailed answers and follow-ups are available directly on this page. Historical milestone statements retain their dates; current corrections below take precedence. First-person examples describe portfolio artifacts, not employment experience. The [study guide](study-guide.md) retains its existing URLs and anchors for compatibility.

[Cross-project technical questions](cross-project-boundaries.md): atomicity, architecture, resource costs, security, testing and recovery.

## Review provenance

Q001–Q005 retain the 2026-10-19 review; Q101–Q106 were updated against source on 2026-11-26. No sibling application tests or services were executed. See the [scope and evidence record](../operations/documentation-audit-2026-10-19.md).

## Engineering Library interview

> Current baseline — 2026-11-26: local MakeDocs/Ollama and managed host publication are implemented. Generated content remains a draft; desired quality and neural fine-tuning are not established. See [current architecture](../architecture/current-implementation.md).

These conceptual comparisons do not imply runtime integration. Implemented facts, general theory and hypothetical alternatives are explicitly separated.

### Q001 — Introductory: What is Engineering Library responsible for?

**Answer:** Implemented: this repository maintains bilingual project documentation and serves it through a Next.js book reader backed by a Rails catalog API. PostgreSQL persists indexed project identity/visibility and shared annotation locations; Markdown remains the source for document bodies and localized bios. `Catalog::Sync` validates both bios before serializing database writes inside a transaction with a PostgreSQL advisory lock. The catalog endpoint pages active projects, while Next reads scoped collection Markdown on the server. This is an implemented local application, with no claim of production deployment, payment flow or full-project AI acceptance.

Follow-up: Why retain old interview answers instead of replacing them with dossiers? Answers teach reasoning and failure analysis, while dossiers explain mechanisms; both are required. Stable additional Q IDs preserve old numbering and bilingual alignment. Follow-up: What is the cost of self-contained explanations? Shared facts are repeated between project docs and library, so source review and explicit gaps must maintain consistency. Links alone would reduce duplication but fail the interview requirement. Semantic accuracy remains manual review; a successful link check cannot prove an answer is true.

### Q002 — Challenging: How does the validator prevent documentation links from becoming unsafe reads?

**Answer:** Implemented: `tools/check_catalog.py` validates the current project-first tree and reuses parsing/path checks from `tools/check_docs.py`. The older validator also supports the former root-language layout; it is not the primary catalog command. Path classification rejects restricted and outside-workspace components and symlinks before document reads. Source links receive existence/metadata checks rather than source execution. Catalog checks add bilingual path/Q-ID parity, retained interview headings, import provenance and graph reachability from the Library and project indexes. Unsafe links are errors in the current catalog wrapper; external URLs are not fetched.

Follow-up: Is it a race-free sandbox? No. lstat followed by read has a TOCTOU window in a maliciously changing filesystem; the tool assumes a cooperative local workspace. A descriptor-based no-follow traversal could strengthen that at portability cost. Follow-up: Does the Markdown parser fully match GitHub? No. It handles a documented subset of inline/reference links, headings, fences and explicit IDs. Complex nested syntax needs manual review. Exit nonzero indicates errors, JSON contains structured findings, and isolated fixtures exercise failure paths. A validator can expose coverage gaps without deciding technical truth or translation quality.

### Q003 — Intermediate: How does the collection represent and validate navigation without deploying an application?

**Answer:** Implemented: stable Markdown paths are the navigation contract. The current catalog validator loads allowed Markdown, extracts anchors/link targets and walks the link graph from the Library and each project-language index. These Python checks run without Rails, PostgreSQL or Next. The running reader has separate behavior: `documentationEntries` unifies relative document IDs across languages, skips navigation-only indexes and retains substantive indexes, then constructs category/document entries. Thus FAQ indexes containing answers become readable chapters automatically. A passing structural check does not demonstrate browser pagination or runtime API availability.

Follow-up: What is the cost? Reading/parsing grows with documentation bytes and graph traversal with vertices/edges, plus filesystem metadata checks; no performance measurements are available. Follow-up: Can structural validation detect conflicting facts or poor translations? No. It can detect IDs/counterparts and missing answers, but source-grounded content review must judge meaning. Isolated tests prove selected safety/parser/failure contracts, not race-free operation under hostile filesystem mutation or external URL reachability.

### Q004 — Why are filesystem content and catalog synchronization separate consistency boundaries?

**Answer:** `Catalog::Sync` validates both bio files and duplicate stable identifiers before entering a PostgreSQL transaction. Its advisory lock serializes cooperating database sync transactions, not filesystem editors. A file may change after validation; subsequent presenters also read bios from disk. Keep metadata stable during sync, and synchronize explicit bio/name/slug changes. Editing a chapter body needs no database ingest. Missing projects become inactive rather than deleted; stable identifiers preserve catalog identity across supported slug renames. This does not migrate bookmarks, whose project association is a slug string. A successful sync therefore establishes the indexed metadata update under those inputs, not an atomic snapshot of every chapter or automatic repair of old bookmark URLs.

### Q005 — What protects shared annotations, and what does it not guarantee?

**Answer:** All browsers use one local PostgreSQL dataset scoped by canonical project, document and mandatory language. Signed, expiring application CSRF tokens and same-origin proxy checks protect mutations without cookies or profiles. IDs identify distinct annotations; preserved legacy bookmarks use a deterministic location variant. The 200-bookmark admission check is not an exact concurrent quota. Document existence is validated, but arbitrary anchor existence is checked when navigating; changed content may make a location unavailable. See [current architecture](../architecture/current-state.md).


## Application and catalog questions

Existing [application FAQ path](application-and-catalog.md) remains available. The complete answers also appear here; current corrections supersede the former scaffold description.

Read [current architecture](../architecture/current-state.md), [future direction](../architecture/future-direction.md) and the [retained questions](study-guide.md). Implemented means inspected source, not execution in this milestone. Proposed alternatives below are analysis, not the author's undocumented original motivation.

### Q101 — Why Rails with a separate Next.js frontend?

**Answer:** Rails handles validated catalog synchronization, relational annotations and guarded operation coordination; Next renders Markdown and manages browser book layout. HTTP separates their runtime responsibilities. Markdown remains the chapter source of truth, while PostgreSQL stores metadata and annotations. The separation adds builds, dependencies and diagnostic boundaries; it does not prove a benchmark win or Clean Architecture.

**Follow-up:** Can the frontend bypass Rails for every feature? It reads chapters on the server, but catalog/annotations/operations use Rails. Shared notes need persistence and logical locations rather than physical page numbers.

### Q102 — What does Compose reproduce, and why is Python needed on the host?

**Answer:** Compose defines frontend, backend, PostgreSQL and Ollama, health dependencies, loopback ports and explicit storage scopes. The host supervisor/adapter is an additional required POSIX process managed by `tools/init_dev_env.py`. It safely acquires external sources and publishes accepted docs without arbitrary new source mounts. Frontend and backend currently mount library docs writable; source/agent mounts have separate restrictions.

**Follow-up:** Does stopping containers erase state? Normal managed stop/down preserves persistent storage. Neither bind persistence nor a successful start proves backup/restore integrity. Do not delete database, model or recovery directories to repair startup.

### Q103 — What does a green health status prove?

**Answer:** `/up` proves Rails response and required adapter heartbeat readiness at that moment. It does not query all catalog records or validate the approved model, generation quality, both publication destinations or restore integrity. Individual PostgreSQL/Ollama/Next health checks have similarly bounded purposes. Catalog API access can synchronize metadata, so it is not a strictly read-only DB probe.

**Follow-up:** Is inference success sufficient? No. Evidence must pass evaluation and ownership checks, library/staged writes must succeed, and required host delivery must complete. A published draft still needs human review.

### Q104 — How are registration, duplicate prevention and relocation handled?

**Answer:** Relative references resolve from the library checkout on the host. Registration verifies source identity and creates metadata/bios without inference. Stable identity, normalized paths, physical aliases and request IDs prevent duplicate retries. Git root-commit identity describes lineage; current file hashes describe content. Relocation requires the same identity at a new path, the previous source confirmed missing and no ambiguous copies.

**Follow-up:** Does changing an unrelated repository's name migrate annotations? No. Verified source relocation preserves supported identity/reference relationships; it is not a generic slug rename, bookmark rewrite or arbitrary metadata migration.

### Q105 — How do local inference and evaluation work today?

**Answer:** The normal caller uses approved `llama3.2:3b` through local Ollama and three integrity-checked skills. It selects bounded source evidence, requests bilingual structured facts, verifies model envelopes/provenance/literals/claims, then renders owned summaries. Automatic Python declaration requests share a bounded deadline. UI and default CLI use `Documentation::Command`; an opt-in project workflow is separate.

**Follow-up:** Is the agent trained to the desired quality? That is not established. Skill context is not neural fine-tuning. Mechanical acceptance can miss semantic mistakes and poor translations; desired quality remains future work requiring a separately authorized campaign. No cloud fallback or automatic replacement model is used.

### Q106 — Can the full registration lifecycle work without existing docs?

**Answer:** The design supports register → generate → update → remove registration → register again → generate again. First publication creates original `docs/` safely. Removal archives the library tree and preserves original source/manual docs, while eligible re-registration restores stable identity/archive. Source disappearance or adapter failure does not justify deleting evidence or automatically dropping a managed registration.

**Follow-up:** What if delivery or removal is interrupted? Pending delivery can be resumed from the saved config without inference; journals and verified archives govern command/removal recovery. Concurrent or ambiguous state fails closed. See [runtime and recovery](../operations/runtime-and-recovery.md). This source review is not a claim that a new complete lifecycle test was executed.
