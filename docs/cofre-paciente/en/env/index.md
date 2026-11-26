# Configuration and per-operation requirements

## Server inputs without values — 2026-11-16

`DB_MONGO_URL` carries the MongoDB URI, authentication database (`authSource`) and any existing TLS/transport options. `DB_MONGO_SELECTION_TIMEOUT_MS` and `DB_MONGO_CONNECT_TIMEOUT_MS` retain their roles. The current application database name remains `cofre_paciente`; it is not newly parameterized.

Infrastructure supplies effective values through the existing configuration interface. This catalog includes no private address, credential, connection string or operational server path.

The source repository maintains its environment contract. This catalog links feature requirements and the reader inventory to avoid copied tables drifting from source. Effective values, credentials, private endpoints and signing material do not belong in the catalog.

- [Configuration / Configuração](../../../../../cofre-paciente/docs/en/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../cofre-paciente/docs/en/guides/environment.md)
- [Implementation / Implementação](../../../../../cofre-paciente/docs/en/architecture/current-implementation.md)
