# Configuração e requisitos por operação

## Insumos de servidor sem valores — 16/11/2026

`DB_MONGO_URL` fornece a URI MongoDB, banco de autenticação (`authSource`) e opções existentes de TLS/transporte. `DB_MONGO_SELECTION_TIMEOUT_MS` e `DB_MONGO_CONNECT_TIMEOUT_MS` mantêm suas funções. O nome de banco da aplicação continua `cofre_paciente`; não foi criada parametrização nova.

A infraestrutura fornece os valores pela interface de configuração existente. Este catálogo não inclui endereço privado, credencial, string de conexão ou caminho operacional de servidor.

O repositório de origem mantém o contrato de ambiente. O catálogo referencia os requisitos por funcionalidade e o inventário de leitores para evitar cópias de tabelas que divergem do código. Valores efetivos, credenciais, endpoints privados e material de assinatura não pertencem ao catálogo.

- [Configuration / Configuração](../../../../../cofre-paciente/docs/pt-br/guides/configuration-contract.md)
- [Environment / Ambiente](../../../../../cofre-paciente/docs/pt-br/guides/environment.md)
- [Implementation / Implementação](../../../../../cofre-paciente/docs/pt-br/architecture/current-implementation.md)
