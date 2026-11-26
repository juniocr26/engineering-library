# Integration boundaries — Cofre Paciente

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

The closed policy contains nine POST paths: links insert/get/update; cartoes insert/get/delete; avaliacoes insert/avaliados/buscar-media-avaliacoes, all under /api/. JwtMiddleware requires HS256, configured credentials, integer iat/exp, positive lifetime at most 60 seconds and current validity. Authentication failure is 401, outer transport failure 422 and operation binding failure 403. Request query strings, wrong methods, wildcard scopes and changed encrypted bytes fail binding. Exact request replay can still pass within token validity.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)
- [Criptografia Lib](../../../criptografia-lib/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Current HTTP / HTTP atual](../../../../../cofre-paciente/docs/en/api/http-contracts.md).
