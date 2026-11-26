# Application, catalog and MakeDocs FAQ

[FAQ index](index.md) · [Current architecture](../architecture/current-implementation.md)

Current source review: 2026-11-26. Answers describe inspected mechanisms, not an additional runtime acceptance test. Existing question IDs are retained for compatibility.

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
