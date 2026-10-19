# Future direction and open design questions

## Status

The read-only catalog API, internal Markdown book reader, project search and anonymous bookmarks are implemented. The [current state](current-state.md) describes their boundaries. Remaining proposals concern automated documentation generation, inference and private/public access policy; the older scaffold roadmap is historical.

## Reading interface

Project selection, bilingual chapter discovery, measured reading pages, source disclosures and logical bookmarks already exist. Remaining work must be derived from concrete reader behavior and test evidence, not a proposal to build the whole reader again. A separate raw-Markdown Rails API is not required by the current design: Next reads the scoped local collection. No production deployment or complete accessibility certification is inferred from this implementation.

## Local AI and incremental generation

A proposed workflow is: discover allowlisted public repositories → inspect safe documentation and relevant source → identify changed inputs → propose evidence-linked documentation changes → validate parity/navigation → review and publish deliberately. This is a design outline, not an installed agent or automation framework. Source hashes and inspected revisions can support change detection, but a changed hash alone cannot identify semantic impact. Preserve human notes and stable question/ADR IDs; compare before rewriting.

Local inference offers data locality and offline operation but consumes CPU/RAM and requires model/runtime management. Commercial APIs can reduce local compute burden but introduce external data transfer, cost and service dependency. Neither provider is integrated. No model, quantization, context length, inference speed or hardware minimum has been selected or measured. Model weights, KV cache, context, concurrency and runtime overhead all affect memory. Benchmark representative safe tasks on the actual host before selecting a model.

## Knowledge consistency and public/private separation

An ingestion adapter should enforce allowed roots without traversing external symlinks, exclude credentials/storage/backups and distinguish implemented code, dated evidence, documented rationale and proposed improvements. These are proposed safeguards, not a deployed security boundary. Separate private inputs, outputs and access policy from the public catalog; never assume a model can reliably redact secrets. A source citation supports traceability but does not establish truth by itself.

Open challenges: source/document drift; conflicting historical milestones; translated meaning versus path parity; robust Markdown links/anchors; review of model hallucinations; preserving authored material; bounded inference resources; and safe publication. Suggested next order is maintain the existing catalog/reader → resolve measured usability and evidence gaps → separately scope ingestion/inference experiments. This is planning, not a release commitment.
