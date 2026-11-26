# Configuration and per-operation requirements

## Server inputs without values — 2026-11-16

`VIVABEM_KEEP_DATA=sim` supports unattended preservation. Interactive yes and no both preserve persistent database data. Some legacy error text still mentions deletion; it does not enable a reset branch. External database credentials remain application-specific and private.

Infrastructure supplies effective values through the existing configuration interface. This catalog includes no private address, credential, connection string or operational server path.

The source repository maintains its environment contract. This catalog links feature requirements and the reader inventory to avoid copied tables drifting from source. Effective values, credentials, private endpoints and signing material do not belong in the catalog.

- [Configuration / Configuração](../../../../../acesso-servidor/docs/en/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../acesso-servidor/docs/en/guides/environment.md)
- [Implementation / Implementação](../../../../../acesso-servidor/docs/en/architecture/current-implementation.md)
