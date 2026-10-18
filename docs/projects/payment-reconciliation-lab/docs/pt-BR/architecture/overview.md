# Arquitetura e domínio

[English](../../en/architecture/overview.md) | [Português](overview.md)

Payment Reconciliation Lab está em transição do estudo Aurora Bakery para reconciliação de pagamentos. A identidade da infraestrutura mudou; a aplicação atual ainda expõe catálogo legado somente leitura. Reconciliação e Stripe são planejados, sem entidades, endpoints, jobs ou chamadas ao provedor implementados. O [relatório de reestruturação](../operations/historical-refactor-report.md) preserva o histórico de comércio, não o roadmap atual.

## Módulos implementados

Spring Boot atende `GET /api/v1/products`. `ProductController` delega ao `CatalogService` transacional somente leitura, que chama o `ProductRepository` concreto Spring Data JPA e mapeia entidades para records `ProductSummary`. É separação pragmática: aplicação importa infraestrutura e entidades usam JPA; não é inversão estrita de dependências.

Produtos mantêm slug/nome/descrição, preço BRL, categoria, metadado opcional de imagem, destaque/disponibilidade e timestamps legados. A consulta inclui AVAILABLE e TEMPORARILY_UNAVAILABLE, ordenando destaque decrescente e nome crescente. `purchasable` só é true para AVAILABLE; é metadado, não compra implementada. DISCONTINUED e ARCHIVED permanecem armazenados e ocultos. Não há paginação, endpoint de escrita, estoque ou upload.

Angular carrega `/products` de forma lazy; chamadas relativas `/api` usam proxy dev para `backend`. Um estado discriminado em signal separa loading, erro, vazio e resultados; retry faz nova requisição. A interface legada e o texto de padaria continuam visíveis. Não existe UI de reconciliação.

Segurança libera GETs explícitos de catálogo/health e OpenAPI no perfil dev, negando demais rotas. CORS define origens/métodos/headers; não há login nem identidade persistida. Código/testes CUSTOMER/ADMIN e política de compra foram removidos. Falhas usam Problem Details genérico no cliente; logs do servidor retêm exceções. Stateless/CSRF desabilitado descreve leitura atual e precisa ser revisto antes de escritas autenticadas.

## Evolução do banco

Flyway preserva V1/V2. V2 renomeia `stores` para `legacy_stores` e cria products com constraints; bancos novos aplicam ambas. Não há migração de reconciliação. Hibernate valida schema; `open-in-view=false` mantém mapeamento na transação do serviço. Preserve checksums e credenciais do banco inicializado na [transição da infraestrutura](../docker/runtime.md).

SQL de seed do catálogo removido. `DevelopmentSeedConfiguration` rejeita `app.seed.enabled=true` com falha no ApplicationRunner: mantenha `DEV_SEED_ENABLED=false`. O runtime base ainda aplica Flyway automaticamente; o override dev o desabilita e exige schema inicializado. Não há geração de fixtures de reconciliação.

## Ciclo de vida e fronteiras planejados

Está estabelecida a direção para reconciliação e integração Stripe de teste. `STRIPE_SECRET_KEY` reservado não tem binding, validação ou SDK consumidor; Compose não o passa ao backend. Entrada no exemplo público não implementa integração.

Antes dos fluxos, defina entradas de reconciliação, regras de correspondência, representação monetária/moeda, divergências, replay/idempotência e revisão autorizada. Eventos assinados, registros financeiros do servidor e tratamento de duplicatas são considerações de estudo, não contratos selecionados/implementados. Cadastro CUSTOMER/ADMIN, fidelidade, checkout da padaria, estados de pedidos e uploads pertencem ao histórico de comércio e não são entregas atuais. Veja [roadmap](roadmap.md) e [decisões](../adr/architecture-decisions.md).

## Sequência de requisição implementada

```mermaid
sequenceDiagram
    participant UI as Angular
    participant API as ProductController
    participant S as CatalogService
    participant DB as PostgreSQL via JPA
    UI->>API: GET /api/v1/products (development proxy)
    API->>S: list()
    S->>DB: visible availability, featured/name ordering
    DB-->>S: products
    S-->>API: ProductSummary DTOs inside transaction
    API-->>UI: JSON array or generic Problem Details
```
