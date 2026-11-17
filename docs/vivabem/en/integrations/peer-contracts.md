# Integration boundaries — VivaBem

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

ClienteHttpCofrePaciente rejects protected claim overrides, unsupported paths, query/fragment/userinfo and redirects; it signs the closed operation map with a maximum 60-second lifetime. It requires both successful HTTP and body status=success, maps connection errors to 504 and other response failures to 500. ClienteHttpCarteiraDigital implements an allowlisted authenticated client for current card, history and purchase/status routes; consultarEstorno remains an unavailable legacy method. AssinadorEventoHub emits RS256 content-bound direct Redis events; recipient session authentication remains a separate capability.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [Carteira Digital](../../../carteira-digital/en/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/en/architecture/contracts.md)
- [Hub VivaBem](../../../hub-vivabem/en/architecture/contracts.md)
- [Criptografia Lib](../../../criptografia-lib/en/architecture/contracts.md)
- [script-auditoria-envs](../../../script-auditoria-envs/en/architecture/contracts.md)
- [VivaBem Android](../../../vivabem-android/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Current HTTP / HTTP atual](../../../../../vivabem/docs/en/api/http-contracts.md).
