# payment-reconciliation-lab: local documentation evaluation

Reviewer-authored verification record, 2026-11-16. It is separate from the local-model generated draft and does not certify complete security, performance or platform support.

## Actual baseline

The complete Maven application package built with JDK 25; test sources compiled but tests were not executed by package -DskipTests. The real HTTP API ran against a new synthetic PostgreSQL 17 database: one product, decimal price, string availability, boolean purchasable and null image were checked; write route returned 403. A pg_dump was restored to an isolated recovery database and product-row JSON matched exactly.

## Reversible scenarios and recovery

Renaming the DTO name component to displayName changed the actual API response. Removing imagePath required adapting both production constructor and one stale test fixture; the first failed test compilation is preserved. The corrected build/API checked absence of imagePath. All experimental sources, fixture bytes and baseline runtime were restored.

Application sources were restored; accepted implementation/documentation changes remain. Both generated destinations use one logical bilingual result. Mechanical validation and quoted code do not prove model prose correct. Execution used Linux containers on a macOS host; Windows/WSL2 and an independent Linux host remain unverified. No model weights were trained.

[Contents](../index.md)
