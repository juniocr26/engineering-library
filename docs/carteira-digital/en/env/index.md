# Configuration and per-operation requirements

## Server inputs without values — 2026-11-16

`DB_CONNECTION`, `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`; retain existing optional `DB_URL`, `DB_SOCKET` and `MYSQL_ATTR_SSL_CA`. Do not reuse another application’s schema or credentials by assumption.

Infrastructure supplies effective values through the existing configuration interface. This catalog includes no private address, credential, connection string or operational server path.

The source repository maintains its environment contract. This catalog links feature requirements and the reader inventory to avoid copied tables drifting from source. Effective values, credentials, private endpoints and signing material do not belong in the catalog.

- [Configuration / Configuração](../../../../../carteira-digital/docs/en/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../carteira-digital/docs/en/guides/environment.md)
- [Implementation / Implementação](../../../../../carteira-digital/docs/en/architecture/current-implementation.md)
