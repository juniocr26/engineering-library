# Catálogo atual, transição de domínio e estudo para entrevista

Revisão estática: 2026-10-18 em `71b8b8f22d38f08e8ab40cb519f8b1a0985b74c6`. Nome e roadmap apontam para conciliação de pagamentos, mas a aplicação inspecionada entrega catálogo somente leitura de uma padaria. Java/Spring Boot, PostgreSQL/Flyway e Angular implementam esse catálogo; Stripe, webhooks, conciliação de liquidações e persistência de pagamentos não estão implementados. O projeto é independente das outras aplicações do portfólio.

## Execute e acompanhe uma requisição

Siga o [setup](setup.md) em clone novo: copie `.env.example` sem sobrescrever configuração existente, configure senha local privada do banco e use o Compose principal. UI: localhost:4200/products; API: localhost:8080/api/v1/products. Startup aplica Flyway e valida mapeamentos JPA. Instalações existentes devem seguir a [transição que preserva dados](../docker/runtime.md); mantenha `DEV_SEED_ENABLED=false`. Esses comandos não foram executados nesta manutenção.

`ProductApi.list()` do Angular chama GET `/api/v1/products` na mesma origem pelo proxy. Spring permite esse GET; `ProductController` chama `CatalogService`, cuja transação somente leitura consulta o repositório JPA e mapeia para `ProductSummary`. Serializar DTOs é diferente de expor entidades JPA. Com open-in-view desabilitado, o mapeamento ocorre no serviço. A UI distingue carregamento, erro, vazio e resultados; retry repete leitura.

V1 é histórico imutável. V2 renomeia a tabela antiga para `legacy_stores`, preserva suas linhas e cria `products` com UUID, slug único e restrito, preço positivo NUMERIC(12,2), estados permitidos e timestamps. Não existe chave estrangeira tenant/store no catálogo novo. Filtro de disponibilidade e política de resposta `purchasable` diferem das constraints SQL. Preservar linhas antigas não prova prontidão de backup/restauração.

## Segurança, falhas e alternativas

Spring Security é stateless, permite apenas GETs selecionados e nega o restante. Swagger é exclusivo de dev. Não há login/JWT ou autorização de pagamentos. CORS permite origens configuradas com GET e sem credenciais; é política do navegador, não identidade do cliente. Desabilitar CSRF precisa ser reavaliado se houver mutações com cookies. Respostas genéricas Problem Details evitam expor diagnósticos internos.

O catálogo não possui paginação nem capacidade medida de consultas. Semântica transacional somente leitura não implica consistência distribuída ou transação futura com provedor. Constraints PostgreSQL protegem linhas locais; um provedor futuro exigiria verificação de assinaturas, tratamento de replay, identidade durável e regras de conciliação. Adaptador de provedor ou outbox seriam propostas, não integrações comprovadas.

## Preparação para entrevista

**Introdutória — O que pode demonstrar hoje?** Leitura do catálogo por Angular, HTTP, serviço/DTO Spring, JPA e PostgreSQL, com allowlist e histórico de migrations. Aprofundamento: explique conciliação planejada separadamente; não alegue chamadas Stripe, criptografia de pagamentos ou resultados financeiros.

**Intermediária — Por que DTOs dentro da transação somente leitura?** Explicitam a resposta e evitam depender de contexto de persistência aberto na serialização. Aprofundamento: uma projeção simples poderia reduzir mapeamento; meça antes de atribuir esse ganho ao projeto. A anotação não é autorização nem prova de ausência de efeitos no startup.

**Desafiadora — Como evoluir o banco com segurança?** Preserve V1/V2 aplicadas, adicione migration forward e mantenha dados históricos necessários. Aprofundamento: rollback de código não reverte migrations; teste restauração em banco descartável e defina compatibilidade antes de alterar identidade persistente. Esses exercícios não foram feitos agora.

[Testes](../testing/strategy.md) separam API/segurança e política de seed de `ProductPostgresIT` com PostgreSQL real; testes frontend exercitam estados de renderização. H2/unidades não demonstram compatibilidade Flyway/PostgreSQL ou rollout produtivo. Consulte [API](../api/catalog-contract.md), [banco](../database/catalog-and-transition.md) e [decisões](../adr/architecture-decisions.md). Permanecem lacunas em todos os fluxos de pagamento, contratos reais de provedor, identidade/TLS de produção, paginação/planos e restauração comprovada. Nenhum teste da aplicação foi executado aqui.
