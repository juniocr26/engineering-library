# Future direction and open design questions

[Architecture index](index.md) · [Current implementation](current-implementation.md)

<!-- reading-section: future-direction-1 -->
## Implemented baseline

Catalog, bilingual reader, search, shared annotations, local Ollama drafting, host filesystem access, explicit lifecycle management and recoverable publication already exist. Earlier proposals to introduce local inference are historical. The normal generator produces bounded source summaries, not every chapter in a reviewed engineering book.

<!-- reading-section: future-direction-2 -->
## Quality and evaluation

The next quality campaign should be scoped separately by the owner. Current evidence/schema/ownership checks do not establish semantic truth, equivalent translation, useful coverage or final editorial quality. Any proposed prompt, skill, dataset, model or fine-tuning change needs its own evidence and authorization. Existing research, checkpoints and learning artifacts must be preserved; no completed neural fine-tuning is claimed here.

<!-- reading-section: future-direction-3 -->
## Access and portability

The installation has shared annotations and local development management, not a public identity system. A production access policy, external exposure and user-specific ownership would need explicit design. Native Windows adapter support is not implemented; the documented Windows execution environment is WSL2. Broader source coverage, retrieval integration and performance guarantees remain questions to validate, not current acceptance claims.

See [decisions and tradeoffs](decisions.md) and [MakeDocs limitations](../training/local-documentation-command.md). Retain dated reports as historical evidence instead of silently reclassifying their results as current verification.
