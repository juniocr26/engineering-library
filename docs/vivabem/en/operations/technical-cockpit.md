# Technical Cockpit: capabilities and public boundaries

[Index](../index.md)

## Verified state and public boundaries — 2026-11-11

Laravel Portal with a Technical Cockpit separate from the Audit Panel. Current navigation includes Overview, Infrastructure, RabbitMQ, Databases, Reconciliations and TracePaw; Executions and Integrations are not separate destinations. Observability queries retained files on demand with project authorization, filters, bounded pagination and incomplete-query indicators. The MySQL SQL generator offers INSERT/UPDATE/SELECT/DELETE for selected rows, including verified composite keys; it produces text for review/copy without automatic execution.

All three consumers declare and lock `parceiro-vivabem/tracepaw-lib 0.2.0`; local installed metadata records the same version. Channel `tracepaw`, namespace `TracePaw` and `tracepaw-YYYY-MM-DD.log` are current contracts. Monolog owns formatting/rotation/retention; the internal JSONL writer is a different adapter. Historical logs remain untouched.

Source inspection and local metadata do not confirm Docker image contents, deployment, mounts or external acceptance. This public summary omits internal endpoints, topology, identifiers and private rules; full operational contracts remain in source repositories. No database catalog synchronization was performed.

Technical access is separate from product login. Administrative actions require authorization and specific safeguards; SQL generation grants no execution privilege. Log queries use HTTP on demand without continuous streaming. Severity, frequent-code and daily metrics describe only complete queries over retained files. Partial queries must not present apparently complete totals. Actual source availability remains unverified. No separate module observing all commands, jobs and Node events live was established; audited administrative operations are not a generic execution-output history.

## Query Plan — 2026-11-12

The Database Explorer includes MySQL estimated plans, measured execution restricted to authorized local environments and MongoDB 7.0 explain with separate planner/statistics modes. Redis has no SQL equivalent. [Diagnostics and execution boundaries](../database/query-plan.md) explains authorization, per-path read-only controls, limits, interpretation and lack of runtime certification.
