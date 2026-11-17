# Configuração e requisitos por operação

## Insumos de servidor sem valores — 16/11/2026

`DB_CONNECTION`, `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`; preservar `DB_URL`, `DB_SOCKET` e `MYSQL_ATTR_SSL_CA` opcionais existentes. Não presumir compartilhamento de schema ou credenciais com outra aplicação.

A infraestrutura fornece os valores pela interface de configuração existente. Este catálogo não inclui endereço privado, credencial, string de conexão ou caminho operacional de servidor.

O repositório de origem mantém o contrato de ambiente. O catálogo referencia os requisitos por funcionalidade e o inventário de leitores para evitar cópias de tabelas que divergem do código. Valores efetivos, credenciais, endpoints privados e material de assinatura não pertencem ao catálogo.

- [Configuration / Configuração](../../../../../carteira-digital/docs/pt-br/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../carteira-digital/docs/pt-br/guides/environment.md)
- [Implementation / Implementação](../../../../../carteira-digital/docs/pt-br/architecture/current-implementation.md)
