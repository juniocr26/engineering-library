# Integration boundaries — acesso-servidor

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

The CLI accepts --validate, --dry-run or --deploy, with --migrate only in deploy. Both validation flags select the same mode and call cleanup_dependencies before preflight: they remove vendor/node_modules in the three PHP projects, Hub node-server/node_modules and four exact .env.audit files. They are not read-only. Deployment branch selection requires existing server refs and rejects dirty/staged/divergent/conflicting trees. Readiness probes are bounded by a validated positive timeout and do not implement rollback.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)
- [Carteira Digital](../../../carteira-digital/en/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/en/architecture/contracts.md)
- [Hub VivaBem](../../../hub-vivabem/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
