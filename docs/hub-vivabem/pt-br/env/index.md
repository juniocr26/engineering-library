# Configuração e requisitos por operação

## Insumos de servidor sem valores — 16/11/2026

`HUB_VIVABEM_REDIS_HOST` e `HUB_VIVABEM_REDIS_PORT` são exigidas pelo overlay de servidor. `HUB_REDIS_PUBLISHER_USERNAME`, `HUB_REDIS_PUBLISHER_PASSWORD`, `HUB_REDIS_SUBSCRIBER_USERNAME`, `HUB_REDIS_SUBSCRIBER_PASSWORD` mantêm papéis ACL separados; o fallback legado suportado é `HUB_VIVABEM_REDIS_PASSWORD`. `HUB_VIVABEM_REDIS_SUBSCRIBE_PATTERNS` mantém a seleção de canais. O cliente Node atual aceita somente a porta Redis `6379`.

A infraestrutura fornece os valores pela interface de configuração existente. Este catálogo não inclui endereço privado, credencial, string de conexão ou caminho operacional de servidor.

O repositório de origem mantém o contrato de ambiente. O catálogo referencia os requisitos por funcionalidade e o inventário de leitores para evitar cópias de tabelas que divergem do código. Valores efetivos, credenciais, endpoints privados e material de assinatura não pertencem ao catálogo.

- [Configuration / Configuração](../../../../../hub-vivabem/docs/pt-br/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../hub-vivabem/docs/pt-br/guides/environment.md)
- [Implementation / Implementação](../../../../../hub-vivabem/docs/pt-br/architecture/current-implementation.md)
