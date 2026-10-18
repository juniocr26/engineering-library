# Implemented catalog API and UI

[English](catalog-contract.md) | [Português brasileiro](../../pt-BR/api/catalog-contract.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

The project name expresses a reconciliation direction; the current business interface is the retained read-only catalog. Angular lazy-loads `/products` and calls relative `GET /api/v1/products`. The development proxy forwards to Spring Boot. `ProductController` delegates to `CatalogService.list`, which uses a read-only transaction and a Spring Data JPA repository, then maps entities to `ProductSummary` records before returning a JSON array. No reconciliation, checkout, order or upload endpoint exists.

The result includes AVAILABLE and TEMPORARILY_UNAVAILABLE, ordered by featured descending and name ascending. DISCONTINUED and ARCHIVED remain stored but hidden. DTO fields include UUID, slug, name, description, BigDecimal price, category, optional imagePath, featured, availability and purchasable. Purchasable is true only for AVAILABLE but does not authorize or execute a purchase. Angular's interface uses a number for price and does not include every server field; its compile-time type does not validate arbitrary HTTP JSON. Loading/error/empty/ready states and manual retry make request outcomes visible.

No pagination, cache or total-count contract exists. The repository materializes all matching entities, then DTOs, and the frontend receives the complete list. This is simple for a small retained catalog but has memory/network/query costs as data grows. Pagination would need stable tie-breaking, cursor/page semantics and UI state; it is hypothetical. Unexpected exceptions return generic 500 Problem Details; logs retain the exception. Do not expose logs or infer a payment failure taxonomy from a generic catalog error.
