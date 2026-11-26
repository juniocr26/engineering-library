# Transações, saldo e idempotência

2026-11-04. O contrato atual de transação possui nove campos com unidades menores inteiras, chave_idempotencia obrigatória globalmente única e metadados estruturados. O enum de 11 casos identifica finalidade separada do estado de aprovação. Saldo permanece decimal; migration posterior de unicidade por titular recusa duplicados sem combinar valores. Locks locais e metadados de efeitos protegem repetição local, sem criar transação com provedor ou Portal.

O repositório de origem mantém detalhes e evidências de código; a revisão foi estática, sem acesso a banco ou provedor.

- [Schema](../../../../../carteira-digital/docs/pt-br/database/transaction-schema.md)
- [Types / Tipos](../../../../../carteira-digital/docs/pt-br/database/transaction-types.md)
- [Structures / Estruturas](../../../../../carteira-digital/docs/pt-br/database/database-audit.md)

[Index / Índice](../index.md)
