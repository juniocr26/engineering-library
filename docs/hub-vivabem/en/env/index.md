# Configuration and per-operation requirements

## Server inputs without values — 2026-11-16

`HUB_VIVABEM_REDIS_HOST` and `HUB_VIVABEM_REDIS_PORT` are required by the server overlay. Existing `HUB_REDIS_PUBLISHER_USERNAME`, `HUB_REDIS_PUBLISHER_PASSWORD`, `HUB_REDIS_SUBSCRIBER_USERNAME`, `HUB_REDIS_SUBSCRIBER_PASSWORD` preserve separate ACL roles; the supported legacy fallback is `HUB_VIVABEM_REDIS_PASSWORD`. `HUB_VIVABEM_REDIS_SUBSCRIBE_PATTERNS` retains channel selection. The current Node client accepts only Redis port `6379`.

Infrastructure supplies effective values through the existing configuration interface. This catalog includes no private address, credential, connection string or operational server path.

The source repository maintains its environment contract. This catalog links feature requirements and the reader inventory to avoid copied tables drifting from source. Effective values, credentials, private endpoints and signing material do not belong in the catalog.

- [Configuration / Configuração](../../../../../hub-vivabem/docs/en/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../hub-vivabem/docs/en/guides/environment.md)
- [Implementation / Implementação](../../../../../hub-vivabem/docs/en/architecture/current-implementation.md)
