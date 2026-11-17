# Transactions, balance and idempotency

2026-11-04. The current transaction contract has nine fields with integer minor units, a required globally unique chave_idempotencia and structured metadados. The 11-case enum identifies purpose separately from approval state. Balance remains decimal storage; a later unique-owner migration refuses duplicates without combining values. Local locking and effect metadata protect repeated local processing but do not create a transaction with the provider or Portal.

The source repository maintains detailed contracts and source evidence; review was static without database or provider access.

- [Schema](../../../../../carteira-digital/docs/en/database/transaction-schema.md)
- [Types / Tipos](../../../../../carteira-digital/docs/en/database/transaction-types.md)
- [Structures / Estruturas](../../../../../carteira-digital/docs/en/database/database-audit.md)

[Index / Índice](../index.md)
