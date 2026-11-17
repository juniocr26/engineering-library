# Startup, implantação e fronteiras dos testes

[English](../../en/operations/deployment-and-evidence.md) | [Português brasileiro](deployment-and-evidence.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

O runtime base aplica Flyway e valida schema. O override de desenvolvimento configura `SPRING_FLYWAY_ENABLED=false`, exigindo schema já inicializado; desabilitar migrações não cria tabelas ausentes. `DEV_SEED_ENABLED=true` ativa runner que falha deliberadamente no startup porque fixtures de conciliação não existem. Mantenha false; não há job de seed para repetir. Compose espera health do banco na base; o override desativa health do backend e muda a dependência do frontend para service_started.

Liveness Spring inclui estado da aplicação; readiness inclui estado e conectividade do banco. Nenhum testa matching, credenciais do provedor ou processamento de webhook. Retry Angular repete GET, não operação financeira. MockMvc substitui serviço de catálogo, Angular substitui HTTP e integração PostgreSQL opt-in usa Testcontainers para migrações/constraints/visibilidade. O inventário atual contém 7 métodos backend unit/API, 5 PostgreSQL e 4 casos Angular; não é percentual de cobertura ou resultado aprovado novo. Nenhum teste de aplicação foi executado aqui.

Preserve credenciais inicializadas e volume real durante a renomeação de infraestrutura. O override existing-db reutiliza volume externo explicitamente em vez de criar substituto silencioso. Antes de atualizar de verdade, revise compatibilidade, produza backup recuperável independentemente, prepare verificação de migração e defina rollback do código com schema compatível. Nenhum desses procedimentos runtime foi executado aqui. Reverter imagem ou arquivo Flyway não restaura dados perdidos. Lacunas incluem rollout/TLS produtivo, restore de backup, planos de consulta de catálogo grande e todo o ciclo de conciliação. Categorias de pagamento devem indicar não implementação, não contratos fictícios de webhook ou ledger.
