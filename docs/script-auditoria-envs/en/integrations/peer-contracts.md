# Integration boundaries — script-auditoria-envs

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

No mode defaults to preview: ordinary invocation writes. `--dry-run` and `--audit-only` both call the ordinary preview path. `--apply-audit` instead merges nonempty `.env.audit` proposals, appends newly introduced names with blank values to the example, and performs mode-specific cleanup without backups. `--selected-directory` requires `--apply-audit`, an existing `.env`, and confines work to that directory. An explicit relative root resolves from the caller; omitted root is the script project parent.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
