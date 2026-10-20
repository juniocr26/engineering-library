# Engineering Library interview

> The complete [technical FAQ](index.md) is the primary entry point for questions and answers. This study document retains historical headings and links for compatibility.

> Source review — 2026-10-19: the current tree implements a Rails catalog API, PostgreSQL catalog records and shared annotations, plus an internal Next.js Markdown reader. The former documentation-only/scaffold description is superseded. No AI agent is implemented. See [current architecture](../architecture/current-state.md).

These conceptual comparisons do not imply runtime integration. Implemented facts, general theory and hypothetical alternatives are explicitly separated.

### Q001 — Introductory: What is Engineering Library responsible for?

**Answer:** Implemented: this repository maintains bilingual project documentation and serves it through a Next.js book reader backed by a Rails catalog API. PostgreSQL persists indexed project identity/visibility and shared annotation locations; Markdown remains the source for document bodies and localized bios. `Catalog::Sync` validates both bios before serializing database writes inside a transaction with a PostgreSQL advisory lock. The catalog endpoint pages active projects, while Next reads scoped collection Markdown on the server. This is an implemented local application, with no claim of production deployment, payment flow or AI ingestion.

Follow-up: Why retain old interview answers instead of replacing them with dossiers? Answers teach reasoning and failure analysis, while dossiers explain mechanisms; both are required. Stable additional Q IDs preserve old numbering and bilingual alignment. Follow-up: What is the cost of self-contained explanations? Shared facts are repeated between project docs and library, so source review and explicit gaps must maintain consistency. Links alone would reduce duplication but fail the interview requirement. Semantic accuracy remains manual review; a successful link check cannot prove an answer is true.

### Q002 — Challenging: How does the validator prevent documentation links from becoming unsafe reads?

**Answer:** Implemented: `docs/validation/check_catalog.py` validates the current project-first tree and reuses parsing/path checks from `tools/check_docs.py`. The older validator also supports the former root-language layout; it is not the primary catalog command. Path classification rejects restricted and outside-workspace components and symlinks before document reads. Source links receive existence/metadata checks rather than source execution. Catalog checks add bilingual path/Q-ID parity, retained interview headings, import provenance and graph reachability from the Library and project indexes. Unsafe links are errors in the current catalog wrapper; external URLs are not fetched.

Follow-up: Is it a race-free sandbox? No. lstat followed by read has a TOCTOU window in a maliciously changing filesystem; the tool assumes a cooperative local workspace. A descriptor-based no-follow traversal could strengthen that at portability cost. Follow-up: Does the Markdown parser fully match GitHub? No. It handles a documented subset of inline/reference links, headings, fences and explicit IDs. Complex nested syntax needs manual review. Exit nonzero indicates errors, JSON contains structured findings, and isolated fixtures exercise failure paths. A validator can expose coverage gaps without deciding technical truth or translation quality.

### Q003 — Intermediate: How does the collection represent and validate navigation without deploying an application?

**Answer:** Implemented: stable Markdown paths are the navigation contract. The current catalog validator loads allowed Markdown, extracts anchors/link targets and walks the link graph from the Library and each project-language index. These Python checks run without Rails, PostgreSQL or Next. The running reader has separate behavior: `documentationEntries` unifies relative document IDs across languages, skips navigation-only indexes and retains substantive indexes, then constructs category/document entries. Thus FAQ indexes containing answers become readable chapters automatically. A passing structural check does not demonstrate browser pagination or runtime API availability.

Follow-up: What is the cost? Reading/parsing grows with documentation bytes and graph traversal with vertices/edges, plus filesystem metadata checks; no performance measurements are available. Follow-up: Can structural validation detect conflicting facts or poor translations? No. It can detect IDs/counterparts and missing answers, but source-grounded content review must judge meaning. Isolated tests prove selected safety/parser/failure contracts, not race-free operation under hostile filesystem mutation or external URL reachability.
