# Architecture decisions and tradeoffs

[Architecture index](index.md) · [Current implementation](current-implementation.md)

This is a source-derived explanation of the current design, reviewed on 2026-11-26. It is not a retroactive claim that alternatives were benchmarked or formally approved in historical ADRs.

| Implemented boundary | Mechanism and practical rationale | Tradeoff / limit |
| --- | --- | --- |
| Markdown bodies, relational metadata | Next reads scoped chapters; Rails synchronizes validated catalog/bios and stores annotations. Files remain editable/reviewable while identities and annotations use relational constraints. | Files and database are different consistency domains; startup/catalog access may synchronize metadata. |
| Separate Rails and Next processes | HTTP API separates persistence/operations from reader rendering and browser layout. | Two dependency graphs, build targets and diagnostic paths; not proof of Clean Architecture. |
| Installation-wide annotations | Logical document/location keys survive physical repagination. | No user identity or private per-user notes; local operation must remain access-controlled. |
| Explicit registration and lineage identity | Relative references plus Git root-commit identity and physical-source checks prevent blind sibling discovery and duplicate/ambiguous relocation. | Repositories sharing lineage need disambiguation; identity does not prove identical working trees. |
| Normal-user host adapter | Bounded requests through private files avoid mounting arbitrary external host trees into the application. Descriptor-based no-follow access constrains acquisition/publication. | Requires POSIX Python and an additional supervised host process; Docker alone is insufficient. |
| Same default generation command | UI coordinator and CLI reuse `Documentation::Command` rather than independently authored generation logic. | Frontend operation/delivery orchestration still differs from direct CLI execution; the opt-in project workflow is separate. |
| Managed outputs and hash ownership | Generated summaries/navigation blocks can be updated while manual content conflicts fail closed. | Manual edits to owned generated output require explicit reconciliation; not a general Markdown merge engine. |
| Journals and recoverable delivery | Before-images, manifests, source hashes and pending delivery support completion/rollback after interruption. | Per-file atomicity is not a distributed transaction; evidence must remain available. |
| Local approved Ollama resources | Manifest and tag/skill hash checks constrain the actual model/context used without cloud fallback. | Locality does not establish privacy of a published draft, semantic correctness, latency or completed fine-tuning. |
| Bounded source facts | Exact declarations, excerpts and schema-bound facts constrain generation and preserve provenance. | Partial coverage and heuristic validation require human factual/translation review. |

<!-- reading-section: decisions-1 -->
## Security and portability consequences

Private repository access, loopback publishing, management-key validation and origin checks protect different boundaries. They do not jointly create a public account system. Shared notes and private source/run evidence need an appropriately restricted installation. Never embed machine-specific source paths, management keys, credential URLs or raw confidential inference envelopes in documentation.

The adapter's case-alias handling confirms physical-file identity rather than lowercasing all paths. This preserves case-sensitive separation while accommodating macOS aliases. Relative references are portable only when the expected checkout relationship and repository identity exist on the new host; they are not absolute-path portability by magic. WSL2 is the required Windows execution environment for this POSIX adapter, with no Windows acceptance claim from this review.

<!-- reading-section: decisions-2 -->
## What remains future work

Desired AI documentation quality, broader useful source coverage, stronger semantic evaluation and any new training/fine-tuning campaign remain separate work. No new public deployment, multi-user identity architecture or universal retrieval pipeline is established here. Existing dated reports remain historical; this explanation does not erase their evidence or authorize implementation changes.

Source references: the [architecture source map](current-implementation.md#source-map), `backend/lib/documentation/command.rb`, `backend/lib/documentation/catalog_management.rb`, `tools/host_filesystem.py`, `frontend/lib/reading-position.ts` and `frontend/lib/note-location.ts`.
