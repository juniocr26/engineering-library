# Catalog schema and domain transition

[English](catalog-and-transition.md) | [Português brasileiro](../../pt-BR/database/catalog-and-transition.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

Flyway V1 creates stores. V2 renames it to `legacy_stores`, preserving rows, and creates `products`. IDs are UUID primary keys; slug is unique with a format CHECK; names/categories must contain non-whitespace content; price is positive NUMERIC(12,2); availability is one of four explicit values; timestamps default to current time. There is no foreign key connecting products to the retained stores and no reconciliation ledger, provider-event or matching table. `updated_at` has a creation default, not a database trigger proving it changes on every update.

JPA uses BigDecimal for price and Hibernate validates schema instead of generating it. `open-in-view=false` means entity mapping must finish inside the service transaction rather than relying on persistence access during serialization. `readOnly=true` is a transaction hint/intent; it is not a replacement for database privileges or authorization. The current service imports the concrete JPA repository, so the layering is useful but not strict dependency inversion.

Unique slug and primary-key indexes serve identity; no catalog filter/sort index is declared by the migrations. Do not claim an optimized query plan without an EXPLAIN and representative data. Monetary scale avoids binary-floating rounding in the persisted catalog, but a real reconciliation domain would also need explicit currency, rounding rules, immutable financial source records, adjustment semantics and matching identities. These are unselected future requirements. Preserve applied migration history/checksums; renaming Compose services or a volume does not transform initialized role/database identity or domain data.
