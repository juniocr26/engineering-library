# adr — rust-event-relay

[Índice do projeto](../index.md)

- [ADR 001 — Usar Rust para o relay](001-use-rust-for-the-relay.md)
- [ADR 002 — Usar PostgreSQL para armazenamento durável de eventos](002-use-postgresql-for-durable-event-storage.md)
- [ADR 003 — Usar Migrações SQL Versionadas para Evolução do Schema PostgreSQL](003-use-versioned-sql-migrations.md)
- [ADR 004 — Usar Tabela Outbox Transacional PostgreSQL para Handoff Durável de Eventos](004-use-postgresql-transactional-outbox-schema.md)
- [ADR 005 — Separar Contratos de Persistência do Relay da Infraestrutura PostgreSQL](005-separate-persistence-contracts-from-postgresql.md)
- [ADR 006 — Publisher RabbitMQ confirmado e Supervisor local](006-rabbitmq-publisher-and-supervisor.md)
- [ADR 007 — Posse durável da entrega com transações curtas](007-durable-delivery-ownership.md)
- [ADR 008 — Política durável de falhas e contratos de recuperação](008-durable-failure-policy.md)
- [ADR 009 — Replay autorizado, idempotente e auditável](009-authorized-idempotent-replay.md)
- [ADR 010 — Efeito atômico de estoque e quarentena pela aplicação](010-atomic-consumer-and-quarantine.md)
- [ADR 011: execuções locais com evidência persistente](011-persistent-demo-runs.md)
- [ADR 012 — ambiente único e cenários reais limitados](012-one-application-real-scenarios.md)
