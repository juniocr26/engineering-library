# Engineering Library: catalog ownership, reader and shared annotations

[Contents](../index.md) | [Português brasileiro](../../pt-br/architecture/current-implementation.md)

Reviewed 2026-11-10. Audience: Rails/Next maintainers and documentation curators. A: source-inspected behavior. Current static verification is separate from Rails/browser execution. The owner identifies this repository/version as private, centralizing documentation from the authorized portfolio and private Viva Bem collections. A separate public version is planned for later.

<!-- reading-section: ownership -->
## Markdown and catalog metadata have different owners

Canonical chapter bodies live in docs/<slug>/{en,pt-br}; API language is en/pt-BR. CATALOG_ROOT and DOCUMENTATION_ROOT must address the same collection. PostgreSQL stores catalog identity and shared annotation records, not canonical chapter bodies. Historical manifest mappings are validator/import metadata, not proof that runtime discovery contains a fixed project count. The newly added TracePaw collection must not be omitted merely because an older provenance inventory predates it.

`Catalog::Files` validates slug/path containment, reads bilingual bios with safe YAML and derives categories from root-index bullets plus existing category indexes. `Catalog::Sync.call` scans immediate valid nonsymlink directories, requires matching English/Portuguese stable ID/name and aborts before writes on invalid/duplicate identities. It uses a transaction/advisory lock, updates by stable_id and deactivates absent projects rather than deleting them. It does not migrate document bookmarks or install redirects after a slug move.

Catalog synchronization is a database mutation, not a Markdown check. A new directory/bio does not prove its metadata is already indexed in the running catalog. No synchronization or annotation mutation was executed here. Do not alter historical import hashes or source snapshots merely to make a validator accept a new collection.

<!-- reading-section: reader -->
## Next discovery, Markdown and navigation

`frontend/lib/documentation.ts` discovers Markdown recursively with containment/symlink checks, excludes bios, handles README identity and suppresses navigation-only indexes. Canonical bilingual document IDs, not translated title order or physical page numbers, drive the contents/reading sequence. Missing translations remain unavailable; matching path sets alone do not prove semantic parity.

`frontend/lib/markdown.ts` parses remark/GFM into semantic units, derives heading slugs and content fingerprints and honors unique reading-section comments or question IDs for cross-language position. Duplicate keys are ambiguous. Document Markdown and note-rich-content rendering are distinct pipelines; installed rehype-raw does not establish raw-HTML support for authored chapters. Use ordinary Markdown, GFM tables and supported Mermaid; preserve existing anchors when editing headings.

Physical book pagination is presentation computed in the browser. PostgreSQL catalog paging is not reader pagination. A successful parser check does not prove that long tables/code paginate correctly on every viewport. No frontend UI or navigation control was changed by this documentation update.

<!-- reading-section: search -->
## Search and approved source references

The document-search GET route trims queries, accepts 2–100 characters, scans the selected project's/language's actual document units and returns at most 80 results with excerpts/anchors and truncated. It uses case-insensitive substring matching, not embeddings, semantic retrieval or PostgreSQL full-text search. Approved integrated source lines can participate through source-search/source-references.

`approvedSource` in source-snapshot.ts is an offline generator gate, not a general runtime machine-file reader. It rejects absolute/traversal/hidden/dependency paths, unsupported extensions, paths outside the real root, binary/oversized files and recognized secret patterns. Size is bounded to 512000 bytes. These checks supplement explicit approval; an approved project does not authorize arbitrary snapshots or publication. No snapshot generation was performed here.

<!-- reading-section: annotations -->
## Shared annotations and security

Rails API exposes projects, bookmarks, highlights, notes and combined annotations. Notes/highlights/bookmarks are shared by installation, scoped by project/document/language, without reader accounts or browser ownership. CSRF is not identity. Development-only note demo routes have explicit mutations and must not be run as harmless verification.

`Note::anchor_key` hashes block/start/end/exact, ignoring relocation prefix/suffix; changes to context alone do not change identity. Note content is UTF-8 and at most 5 MiB, with logical segments validated through Highlight. Associated highlight must match the same location. Schema FK nullifies note highlight_id when a highlight is removed, preserving the note. Bookmarks use logical location plus location_variant; notes are user annotations, not canonical technical chapters.

The schema declares identity/scope indexes and constraints; this is not a measured performance claim or proof of effective deployment privacy. Keep notes, source references, exports and logs within approved private boundaries. Do not add hidden reader identities to explain shared data.

<!-- reading-section: operations -->
## Operations, verification and future retrieval

Existing Compose uses PostgreSQL/Rails/Next and a multi-target Dockerfile. Application commands belong in existing approved runtimes; host Python static checks are available without Docker. Startup/dependency installation and catalog/database preparation have side effects and were not invoked. [Verification](../testing/documentation.md) distinguishes 28 passing fixture tests from unexecuted Rails/browser checks and historical results.

Ollama/RAG, embeddings and assisted generation remain future direction, not implemented search infrastructure. The preserved [documentation standard](../training/documentation-standard.md) owns evidence labels, bilingual rules, templates and future retrieval guidance; this chapter does not shorten or replace it.

Sources: backend/app/services/catalog/{files,sync}.rb, backend/config/routes.rb, backend/db/schema.rb, backend/app/models/note.rb; frontend/lib/{documentation,markdown,source-snapshot}.ts; frontend/app/api/document-search/[project]/route.ts; frontend/package.json; tools/check_docs.py and tools/check_catalog.py. Recheck both languages after discovery, identity, parser, annotations, search or privacy changes. Historical audit/validation documents retain their dates and do not establish current runtime acceptance.
