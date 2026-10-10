# Payment Reconciliation Lab technical interview study guide

[English](payment-reconciliation-lab.md) | [Português brasileiro](../../pt-BR/interviews/payment-reconciliation-lab.md)

Use the [current architecture](../../../../payment-reconciliation-lab/docs/en/architecture/overview.md), [decisions](../../../../payment-reconciliation-lab/docs/en/adr/architecture-decisions.md) and [test inventory](../../../../payment-reconciliation-lab/docs/en/testing/strategy.md). The project is a portfolio lab transitioning from bakery commerce toward reconciliation; it is not an implemented payment platform. Suggested answers are implementation-grounded; rationale is interpretation, and alternatives below are study options rather than historical evaluations. No runtime commands were executed in this audit.

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

The [external-volume transition](../../../../payment-reconciliation-lab/docs/en/docker/runtime.md) reuses an inspected volume and refuses to create a missing replacement. Never interpret the new project name as automatic data movement. These are documented instructions, not operations performed here. Costs include legacy names/tables/UI until a separate domain migration. A new database would simplify naming but require an explicit migration/recovery strategy.

## 4 Security and startup failures

**Question: How are writes protected without login?**

**Model answer:** “Only specific public GETs and dev OpenAPI are allowed; remaining routes are denied. There is no login or authenticated administrator. CORS specifies origins and GET methods, while unexpected failures return generic Problem Details. Server logs still include exception diagnostics.”

CORS is not authentication. Stateless/CSRF-disabled configuration fits the current read boundary; future cookies/tokens require a deliberate security design. The base runtime applies Flyway; the development override disables it and requires existing schema. `DEV_SEED_ENABLED=true` now registers a runner that fails startup rather than inserting fixtures. Disabling the flag prevents that failure; it does not implement reconciliation seeds.

The Angular retry button issues a new request; it is not offline recovery or automatic retry. Database errors become generic 500 client responses. Readiness includes database connectivity but does not demonstrate reconciliation/provider health. Stripe has no SDK, binding or webhook, and Compose does not inject the reserved key.

## 5 Tests and evidence

Source inventory: 5 ProductApiTest methods, 2 seed-guard methods, 5 opt-in PostgreSQL methods and 4 Angular cases. MockMvc replaces CatalogService; Angular replaces HTTP. PostgreSQL integration owns a Testcontainers database and checks migrations, constraints, visibility and health/docs. Fakes do not prove PostgreSQL behavior; those real tests require Docker and were not run here. There are no current pricing, repeatable-seed, reconciliation or Stripe tests. [Verification](../../../../payment-reconciliation-lab/docs/en/testing/verification.md) separates earlier runtime results from this static review.

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

No item is marked studied or completed by this guide. See the [current roadmap](../../../../payment-reconciliation-lab/docs/en/architecture/roadmap.md); earlier bakery delivery commitments do not carry over automatically.

## Additional source-grounded interview deep dives

Original questions and answers above are preserved. IDs below identify this additional sequence; they do not renumber the retained material. Levels guide rehearsal, not implementation status. Follow-ups include answers so this sequence is self-contained.

### Q001 — Introductory: How do you defend the project without presenting planned payments as implemented?

**Answer:** Implemented: a Spring Boot/Angular/PostgreSQL read-only product catalog remains while infrastructure identity transitions to Payment Reconciliation Lab. The API reads visible availability states, sorts them and maps entities to DTOs; the UI presents loading/error/empty/ready states. Reconciliation entities, matching, provider calls, signed webhooks and ledger flows are absent. The reserved Stripe setting is not consumed or passed by Compose. The retained bakery language is legacy UI, not evidence that old checkout commitments survived the transition.

Follow-up: What is still technically valuable? Layer boundaries, transaction-scoped DTO mapping, migration preservation, SQL constraints, deny-by-default HTTP access and isolated testing are concrete mechanisms to explain. Follow-up: What must be decided before implementing reconciliation? Source-of-truth records, matching identity, currencies/amount semantics, discrepancy states, replay and authorized review. Those requirements are hypothetical and unselected. An honest defense connects current mechanisms to possible future needs without inventing delivery, production outcomes or historical motivations. A filename, environment key or roadmap entry is weaker evidence than a callable implementation path.

### Q002 — Intermediate: Why map DTOs inside the service transaction with open-in-view disabled?

**Answer:** Implemented: `CatalogService.list` is read-only transactional, calls a concrete JPA repository and constructs ProductSummary records before returning. With open-in-view=false, HTTP serialization should not depend on later persistence access. The DTO deliberately selects the public representation and derived purchasable value rather than exposing the entity's complete shape or lifecycle. This makes API contracts easier to evolve but requires mapping maintenance. The application still imports infrastructure and entities use JPA, so this is pragmatic layering, not strict dependency inversion.

Follow-up: Does readOnly forbid every database write? It is a framework transaction hint/intent, not an authorization policy or universal SQL write ban. Restrict database permissions and API operations separately. Follow-up: Where could an N+1 problem appear? If future lazy relationships were accessed per entity during mapping; the current retained catalog has no demonstrated such relation/query. JDBC could make SQL explicit; a repository port could decouple application code at extra types/mapping cost. Neither is delivered by this documentation review. Mocking the service at HTTP level cannot verify the transaction or generated SQL.

### Q003 — Intermediate: Which catalog invariants belong to SQL and which belong to response policy?

**Answer:** Implemented: SQL enforces UUID identity, unique formatted slug, nonblank name/category, positive NUMERIC(12,2) price and the availability set. The repository chooses which availability values are visible and their ordering; Product derives purchasable for AVAILABLE only. Database validity therefore does not imply public visibility or a real purchase authorization. V2 preserves stores as legacy_stores without a product foreign key. Timestamp defaults initialize values; no migration trigger guarantees updated_at changes on each update.

Follow-up: Does BigDecimal complete a financial model? No. It avoids binary-floating representation in Java price values, but reconciliation needs explicit currency, rounding, adjustments and source record semantics. Angular currently types price as number; display convenience is not exact client-side financial arithmetic. Follow-up: Would adding an index necessarily speed every query? No. No dedicated filter/sort index is declared here; selectivity, ordering and data size determine benefit and maintenance cost. An EXPLAIN and representative measurements would be separate runtime work. Current docs cannot claim optimized plans or measured scaling.

### Q004 — Challenging: Why are CORS and statelessness insufficient for future payment operations?

**Answer:** Implemented: SecurityConfiguration permits only explicit product/health GETs and dev OpenAPI, denies other requests and returns generic 403. CORS lists origins, GET and selected headers with credentials disabled. This restricts browser behavior and current routes; there is no login, administrator or provider identity. Stateless session configuration says how server sessions are managed, not who a request represents. Disabled CSRF is aligned with this read-only surface, not blanket approval for future cookie-authenticated writes.

Follow-up: Could a non-browser caller bypass CORS? It does not enforce browser CORS at all; server authorization must still hold. Follow-up: How would signed webhooks fit? Hypothetically verify the exact provider-signature contract against the required raw body, constrain replay, store provider-event identity and coordinate deduplication with financial effects. TLS protects transit; signature authenticates event provenance; identity authorizes user operations. They are distinct. There is no implemented Stripe SDK/webhook to defend here, and no provider-specific timeout or signature policy can be invented from a reserved environment key.

### Q005 — Challenging: How can infrastructure renaming and rollback preserve data?

**Answer:** Implemented: Flyway V1/V2 stay intact and retain legacy rows. Hibernate validates; base startup applies Flyway while the development override disables it. A renamed Compose project can select a different volume, but does not rename PostgreSQL roles/databases inside an initialized volume. The existing-db override deliberately references an external volume so absence fails rather than silently creating empty storage. Preserve initialized credentials and verify the intended data location before runtime changes. These procedures were not executed during this review.

Follow-up: Can we edit V1 to match the new product name? Applied migration checksums/history must remain stable; evolve with new migrations. Follow-up: Does rolling back the app image restore data? No. Schema compatibility and separately recoverable backups matter; down migration or volume reset can lose data. A safe future rollout needs a tested migration path and a rollback/forward-fix strategy. The retired seed flag now fails startup when enabled; correcting configuration is the remedy, not retrying a nonexistent seed. Production recovery and backup restore remain evidence gaps.

### Q006 — Intermediate: What tests and performance limits can you defend now?

**Answer:** Implemented evidence: 5 ProductApiTest methods replace CatalogService, 2 tests cover seed rejection/default behavior, 5 opt-in PostgreSQL methods use isolated Testcontainers and 4 Angular cases replace HTTP. The layers prove different things: API fakes cover response/security/error contracts; real PostgreSQL cases exercise migrations/constraints/query visibility; Angular cases exercise UI states. Counts are an inventory, not current passing status or coverage percentage. No application tests ran in this review, and there are no reconciliation/provider tests.

Follow-up: Could all fake tests pass while startup fails? Yes, for missing schema under disabled migrations, wrong credentials or enabled retired seed. Follow-up: What is the actual catalog scaling limit? The query returns all visible entities and DTOs without pagination/cache. Memory, sort work and response size can grow with catalog size; no measured threshold is available. Hypothetical pagination needs stable ordering/tie-breaking and UI contracts, while caching needs an invalidation/freshness policy. Health readiness checks database connectivity but neither these scaling limits nor payment functionality. Test new requirements at the boundary they rely on.

