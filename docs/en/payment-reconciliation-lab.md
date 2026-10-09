# Payment Reconciliation Lab technical interview study guide

[English](payment-reconciliation-lab.md) | [Português brasileiro](../pt-BR/payment-reconciliation-lab.md)

Use the [current architecture](../../../payment-reconciliation-lab/docs/en/architecture.md), [decisions](../../../payment-reconciliation-lab/docs/en/architecture-decisions.md) and [test inventory](../../../payment-reconciliation-lab/docs/en/testing.md). The project is a portfolio lab transitioning from bakery commerce toward reconciliation; it is not an implemented payment platform. Suggested answers are implementation-grounded; rationale is interpretation, and alternatives below are study options rather than historical evaluations. No runtime commands were executed in this audit.

## 1 Project introduction

**Question: What problem does this project address today?**

**Model answer:** “The intended new problem is payment reconciliation, but the current interface is still a retained read-only catalog. Infrastructure uses the Payment Reconciliation Lab identity; Spring Boot, Angular, PostgreSQL and existing migrations remain. Reconciliation, matching and Stripe integration are planned, so I demonstrate current layering, data preservation and HTTP boundaries without claiming completed financial workflows.”

Purchase policy, CUSTOMER/ADMIN vocabulary and catalog seed were removed. The old bakery roadmap and previous test results are historical. A reserved Stripe example setting does not create a provider integration.

## 2 Architecture and request flow

Angular lazy `/products` → relative `/api/v1/products` → development proxy → `ProductController` → read-only transactional `CatalogService` → JPA `ProductRepository` → PostgreSQL → DTO array → loading/error/empty/ready UI.

**Question: Is it Clean Architecture?**

**Model answer:** “It separates API, application, domain and persistence, but the application imports a concrete infrastructure repository and Product uses JPA. This is pragmatic framework layering. DTO mapping protects the public response from entity details; strict dependency inversion would need another port and adapter.”

The list includes AVAILABLE/TEMPORARILY_UNAVAILABLE, sorted featured/name, while discontinued/archived rows remain hidden. `purchasable` is legacy metadata without a purchase endpoint. All visible rows are loaded; no pagination/cache exists. Smaller server-rendered HTML could serve this read API with less frontend tooling; explicit JDBC could offer direct SQL control instead of ORM. Neither is claimed as previously prototyped.

## 3 Schema and preserved data

**Question: Why keep legacy migrations and tables?**

**Model answer:** “V1/V2 remain unchanged for existing Flyway installations. V2 renames stores to legacy_stores and creates products instead of deleting historical rows. Hibernate validates the schema. Renaming infrastructure does not rename initialized PostgreSQL roles/databases or migrate domain data.”

The [external-volume transition](../../../payment-reconciliation-lab/docs/en/docker.md) reuses an inspected volume and refuses to create a missing replacement. Never interpret the new project name as automatic data movement. These are documented instructions, not operations performed here. Costs include legacy names/tables/UI until a separate domain migration. A new database would simplify naming but require an explicit migration/recovery strategy.

## 4 Security and startup failures

**Question: How are writes protected without login?**

**Model answer:** “Only specific public GETs and dev OpenAPI are allowed; remaining routes are denied. There is no login or authenticated administrator. CORS specifies origins and GET methods, while unexpected failures return generic Problem Details. Server logs still include exception diagnostics.”

CORS is not authentication. Stateless/CSRF-disabled configuration fits the current read boundary; future cookies/tokens require a deliberate security design. The base runtime applies Flyway; the development override disables it and requires existing schema. `DEV_SEED_ENABLED=true` now registers a runner that fails startup rather than inserting fixtures. Disabling the flag prevents that failure; it does not implement reconciliation seeds.

The Angular retry button issues a new request; it is not offline recovery or automatic retry. Database errors become generic 500 client responses. Readiness includes database connectivity but does not demonstrate reconciliation/provider health. Stripe has no SDK, binding or webhook, and Compose does not inject the reserved key.

## 5 Tests and evidence

Source inventory: 5 ProductApiTest methods, 2 seed-guard methods, 5 opt-in PostgreSQL methods and 4 Angular cases. MockMvc replaces CatalogService; Angular replaces HTTP. PostgreSQL integration owns a Testcontainers database and checks migrations, constraints, visibility and health/docs. Fakes do not prove PostgreSQL behavior; those real tests require Docker and were not run here. There are no current pricing, repeatable-seed, reconciliation or Stripe tests. [Verification](../../../payment-reconciliation-lab/docs/en/verification.md) separates earlier runtime results from this static review.

**Follow-up:** Does a test count establish coverage or passing status? No: inventory is not execution, coverage percentage or proof of absent workflows.

## 6 Decisions and deeper questions

| Decision | Benefit | Cost / alternative for study |
| --- | --- | --- |
| Retain read-only catalog during transition | Preserves a working code foundation | New domain/UI unfinished; immediate replacement needs new contracts |
| JPA/Flyway/DTO layering | Constraints, versioned schema and explicit API | Framework coupling; JDBC/ports could increase explicitness |
| Deny unmatched/writing routes | Restricts current API surface | No real identity/authorized writes yet |
| Reject retired seed flag | Stale configuration fails visibly | Startup requires flag correction; fixtures absent |
| Preserve initialized volume/migrations | Avoids automatic destructive rename | Legacy database names and tables remain |

Practice: Where does the transaction end? Why is open-in-view disabled? What does readiness prove? Why is a reserved env variable not a feature? How would financial reconciliation differ from catalog price formatting? Which source records and currency/matching rules must be defined before a schema? How would signed events, idempotency and replay be tested in isolated fixtures?

## 7 Ordered study roadmap

1. Explain the truthful current/new/historical scope before describing architecture.
2. Trace controller/service/repository/DTO and Angular states.
3. Read V1/V2 and volume-transition documentation; separate schema identity from Compose identity.
4. Read security and seed guard, then their tests; distinguish inventory from previous execution.
5. Study reconciliation inputs, money/currency, matching and discrepancy semantics as unselected future requirements.
6. Discuss provider boundaries, signature verification, idempotency/replay and access only after defining the domain.

No item is marked studied or completed by this guide. See the [current roadmap](../../../payment-reconciliation-lab/docs/en/roadmap.md); earlier bakery delivery commitments do not carry over automatically.
