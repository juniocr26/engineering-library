# Card-reference lifecycle

Credit/debit collections are separate. Minimal encrypted references reject sensitive fields. Observed deletion protects concurrent replacement; production debit/expired cleanup requires provider confirmation through Wallet where implemented. Legacy unreadable-envelope cleanup is a distinct branch. Reading older test-only limitations as current is incorrect. Source behavior does not establish provider homologation.

[Current implementation / Implementação atual](../../../../../cofre-paciente/docs/en/architecture/current-implementation.md) · [Tests / Testes](../../../../../cofre-paciente/docs/en/testing/testing.md).

Credit does not perform the additional sub check implemented for debit. Manual credit deletion does not perform the provider confirmation used by production debit deletion. These differences are limitations of current source, not equivalent authorization guarantees.

[HTTP / Titularidade](../../../../../cofre-paciente/docs/en/api/http-contracts.md).
