# Future direction and open design questions

## Status

These are requirements and exploratory design proposals for the next milestones, not implemented features or proof of an approved detailed architecture. The current scaffold and Markdown catalog are described in [current state](current-state.md). Existing application-development guidance names a first read-only collection/chapter API as future work.

## Reading interface

The intended technical-book experience starts with project selection, then language, chapter index and document. A future API must define stable identifiers, safe path resolution, Markdown rendering, navigation and error contracts before the Next.js UI consumes it. Existing headings and paths can supply navigation; no search engine, database schema or frontend behavior was added here. Accessibility, code/diagram rendering and broken-link behavior need explicit acceptance criteria.

## Local AI and incremental generation

A proposed workflow is: discover allowlisted public repositories → inspect safe documentation and relevant source → identify changed inputs → propose evidence-linked documentation changes → validate parity/navigation → review and publish deliberately. This is a design outline, not an installed agent or automation framework. Source hashes and inspected revisions can support change detection, but a changed hash alone cannot identify semantic impact. Preserve human notes and stable question/ADR IDs; compare before rewriting.

Local inference offers data locality and offline operation but consumes CPU/RAM and requires model/runtime management. Commercial APIs can reduce local compute burden but introduce external data transfer, cost and service dependency. Neither provider is integrated. No model, quantization, context length, inference speed or hardware minimum has been selected or measured. Model weights, KV cache, context, concurrency and runtime overhead all affect memory. Benchmark representative safe tasks on the actual host before selecting a model.

## Knowledge consistency and public/private separation

An ingestion adapter should enforce allowed roots without traversing external symlinks, exclude credentials/storage/backups and distinguish implemented code, dated evidence, documented rationale and proposed improvements. These are proposed safeguards, not a deployed security boundary. Separate private inputs, outputs and access policy from the public catalog; never assume a model can reliably redact secrets. A source citation supports traceability but does not establish truth by itself.

Open challenges: source/document drift; conflicting historical milestones; translated meaning versus path parity; robust Markdown links/anchors; review of model hallucinations; preserving authored material; bounded inference resources; and safe publication. Suggested order is catalog maintenance → read-only document contract → book interface → separately scoped ingestion/inference experiments. This order expresses prerequisites, not completed milestones or release commitments.
