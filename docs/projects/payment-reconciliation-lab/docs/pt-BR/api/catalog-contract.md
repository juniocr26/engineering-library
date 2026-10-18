# API e UI de catálogo implementadas

[English](../../en/api/catalog-contract.md) | [Português brasileiro](catalog-contract.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

O nome do projeto expressa a direção de conciliação; a interface de negócio atual é o catálogo legado somente leitura. Angular carrega `/products` sob demanda e chama `GET /api/v1/products` relativo. O proxy de desenvolvimento encaminha ao Spring Boot. `ProductController` delega a `CatalogService.list`, que usa transação somente leitura e repositório Spring Data JPA, mapeando entidades para records `ProductSummary` antes de retornar array JSON. Não há endpoint de conciliação, checkout, pedido ou upload.

O resultado inclui AVAILABLE e TEMPORARILY_UNAVAILABLE, ordenado por featured decrescente e nome crescente. DISCONTINUED e ARCHIVED continuam armazenados, mas ocultos. O DTO inclui UUID, slug, nome, descrição, preço BigDecimal, categoria, imagePath opcional, featured, availability e purchasable. Purchasable é true apenas para AVAILABLE, mas não autoriza nem executa compra. A interface Angular usa number para preço e não inclui todos os campos do servidor; o tipo de compilação não valida JSON HTTP arbitrário. Estados loading/error/empty/ready e retry manual tornam resultados visíveis.

Não há paginação, cache ou contrato de contagem total. O repositório materializa todas as entidades correspondentes e depois DTOs; o frontend recebe a lista completa. É simples para catálogo pequeno legado, mas memória/rede/consulta crescem com dados. Paginação exigiria desempate estável, semântica de cursor/página e estado da UI; é hipotética. Exceções inesperadas retornam 500 Problem Details genérico; logs retêm a exceção. Não exponha logs nem derive taxonomia de falhas de pagamento de um erro genérico de catálogo.
