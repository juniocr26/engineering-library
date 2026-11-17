# Query Plan: diagnostics with execution boundaries

Private implementation reviewed on 2026-11-12, presented as an engineering pattern. Examples are synthetic; policies, endpoints and server identities remain internal. [Index](../index.md) · [Cockpit](../operations/technical-cockpit.md).

## Three distinct actions

| Action | Effect and evidence |
| --- | --- |
| Explain | Obtains strategy/estimates without returning query rows as business results |
| Query | Executes a read and returns data subject to separate authorization/limits |
| Analyze execution | Executes an instrumented query; consumes resources even in read-only transactions |

The Database Explorer has an editor and Query Plan tab beside record views. Estimated plans can load when the tab opens; measurement requires explicit action. Changing query, connection, database or object invalidates context. Discarding stale HTTP responses prevents displaying the wrong plan without guaranteeing immediate database cancellation.

This module is one part of the Cockpit, not an automatic optimizer. Other administration actions can modify data/structure; a read tab does not make the entire explorer read-only. SQL generation does not grant execution privileges either.

## Estimated and measured MySQL

The inspected estimated path attempts EXPLAIN FORMAT=JSON in a read-only transaction and falls back to tabular output only for specific syntax/feature errors. Size/row limits prevent unbounded responses; the visual normalizer rejects tabular fallback because it lacks the required JSON hierarchy. Handler duration is not actual execution time of the explained SELECT.

The filter accepts one SELECT or nonrecursive read-only WITH query with permitted functions. It rejects comments, variables, multiple statements, writes, locks and features outside its subset. This defensive validation can reject legitimate SQL and replaces neither database validation nor least-privilege accounts.

Observed measurement uses EXPLAIN ANALYZE FORMAT=TREE and requires MySQL 8.0.21+ within the 8.0 series, local environment and policy matching the actual connection/server identity. A parser accepting earlier TREE versions does not broaden executor support. Do not claim generic MariaDB, other MySQL-series or PostgreSQL support.

Measured execution uses a dedicated connection and read-only transaction, rejects cross-schema access and discovered objects outside its allowed subset, and applies approximately a one-second database limit. Exclusive lock and request UUID with temporary history control concurrency/repetition. Warnings, interruption or malformed output prevent presenting a completed measurement. Finally releases resources. These safeguards reduce risk without making execution free or immediately cancelling it when the browser closes.

## MongoDB and Redis

The observed explain adapter is limited to MongoDB 7.0.x. It accepts find, aggregate, count and distinct on authorized collections with allowed operators/stages. Writes, JavaScript, views, cross-database access and output stages such as $out/$merge are rejected. Pipelines/responses have size/depth limits.

queryPlanner provides planning without execution statistics. executionStats and allPlansExecution execute analysis and require explicit action, authorized local identity, time limits, concurrency/rate controls and a non-reused UUID. Incomplete responses are rejected. Candidate statistics in allPlansExecution can be partial: do not compare them as if every alternative ran completely.

Redis has no equivalent SQL plan in this module. An unsupported-feature message is correct; do not invent EXPLAIN for keys. Other Redis use for diagnostic cache/locks is distinct from the explored connection.

## Interpret without inventing optimization

The frontend normalizes plans into a graph/details while retaining original properties. Depending on output, MySQL exposes tables, access methods, selected/candidate indexes, estimated cardinality, filters, costs, joins, sorting, temporary tables and materialization. Missing values should remain missing. Heuristic diagnostics do not automatically create indexes or guarantee optimization.

Laboratory example using a fictional table:

```sql
SELECT category, COUNT(*)
FROM sample_events
WHERE active = 1
GROUP BY category;
```

Check selectivity and volume before treating a scan/index as good or bad. Filesort does not necessarily mean disk writes; a temporary table does not establish a bottleneck; cost is not milliseconds. Compare estimated/actual values only within the same iterator. TREE times include children and are per loop: summing parent/child times double-counts. Do not assume automatic JSON/TREE node correspondence.

An instrumented query measures one execution with specific cache, concurrency and data conditions. It does not certify future latency. Retain context/hash/timestamp and identify previous plans preserved after failed refresh. Do not convert errors into empty plans or missing metrics into zero.

## Security, errors and validation

Technical sessions and enabled-connection lists restrict access; database accounts retain their own privileges. The application does not grant permissions automatically. Read queries can reveal data/object names; plans and exports require private handling. Local measurement policies must check the effective server rather than a development label alone.

Distinguish rejected queries, unauthorized connections, missing objects, concurrency, rate limits, timeouts and unavailability. Do not automatically repeat measurement after an uncertain response. UI should require another action and avoid presenting partial results as complete.

Handlers, validators, executors, interpreters and presentation were inspected; no current dedicated Query Plan suite was found. No EXPLAIN, ANALYZE, grant, benchmark or browser test was executed. Future checks should use authorized environments, synthetic data and accepted/rejected queries, covering timeout, context changes and partial failures. This is validation guidance, not a claim of completed tests or authorization for new infrastructure.
