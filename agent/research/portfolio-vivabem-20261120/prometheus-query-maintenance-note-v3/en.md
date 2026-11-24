# Prometheus maintenance: timeout policy, estimation order and caller context

`prometheus/prometheus`: `5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4` → `80cd8d97bdfce88014a652d15723559d00a15902`

CANDIDATE_FOR_SOURCE_REVIEW · not owner-approved, Gold or training data.

## A real API revision, not a runtime experiment

This note compares the selected parent/child revisions of development-exposed Prometheus. The commit changes thirteen files; eighteen selected before/after source, test, documentation and license files are preserved. Twenty-three native complete declaration quotes and four manually selected test spans bind the analysis to source. No actual request, database, upstream test, benchmark or Go compilation ran. The paired clauses were authored after inspection; they are not blind predictions or an autonomous maintenance-agent result.

## HTTP timeout is not a cost-limit override

Before, `API.queryTimeout` rejects a positive request above a positive effective ceiling. After, it parses the parameter and rejects nonpositive values but no longer performs that ceiling comparison. `max_query_duration` remains a different per-query override; when the query-cost feature is enabled, the after API also explicitly rejects its negative values. With that feature disabled, the selected option extractor ignores these cost overrides. Do not document the two parameters as sharing the same above-ceiling rejection rule after this revision.

## Parsing acceptance does not disable execution deadlines

A longer positive HTTP timeout is accepted by the after parser, not a promise of unlimited execution. The unchanged selected engine still creates its execution context from its own timeout or stored deadline. Under the standard Go context contract, deriving a later deadline does not extend an earlier parent deadline. Effective server behavior still depends on feature/configuration state and the actual engine implementation; parser code alone does not prove a global cap for arbitrary collaborators.

## The estimator moves before execution

Before, successful `Exec` is followed by `costComparison`. After, both handlers record `limitStart`, build the query, call `estimateForComparison` when cost comparison is enabled, and only then call `Exec`. `pendingCostComparison.finish` later pairs the estimate with actual statistics. This changes caller orchestration even though the engine file is byte-identical. The selected after order avoids holding a finished query result while this estimation waits for its slot; no memory or speed improvement was measured.

## An explicit start differs from resetting a timer

Before, the estimator derives its cost context with `WithTimeout` when it starts. After, it uses `WithDeadline` at `limitStart.Add(duration)`, where the executed-query handlers sampled the start before construction. This avoids granting a fresh full estimation duration after construction. API and engine timestamps are separate samples, and their configurations can differ; this source review does not equate their exact deadlines or prove every collaborator stops at expiration.

## An estimation warning does not guarantee query success

On the selected successful execution path, `pendingCostComparison.finish` merges estimator annotations and turns an estimation error into a warning with no comparison. But `Exec` still runs using its request/engine context and can fail independently. Execution-error returns occur before that finish call and do not merge the pending estimation annotations there. The changed test declaration distinguishes an estimation-only duration failure from a request timeout or cancellation; the former can preserve success in its fixture, which does not install the same duration ceiling on the engine.

## Construction preserves selected typed error categories

Before, `queryConstructionError` handles an above-ceiling error specially and otherwise wraps the error as an invalid query parameter. After, it also recognizes `ErrQueryTimeout` and `ErrQueryCanceled` and delegates those cases to the unchanged `returnAPIError`. This does not classify every raw context error or arbitrary custom-engine error the same way. The source change supports documenting these selected typed paths; it is not an observed HTTP status result.

## Unchanged callees do not imply unchanged documentation

The engine file and the complete native quotes for `queryCostCeilings`, `costRequested` and `returnAPIError` match byte for byte across this pair. Their callers nevertheless change deadline validation, estimation order and construction-error routing. Clauses describing those changed policies require `MODIFY`; source pins also need updating for a new target. Do not infer a whole-chapter `NO-OP` or remove the chapter solely because the old `costComparison` helper disappears and is replaced.

## Existing documentation remains a bounded review

The initial revision comparison preserved eighteen selected before/after files. Follow-up H76–H79 traces now address selected rule, remote-estimate, duration-error and sample-accounting subtopics with separately frozen sources. They do not accept three large pages wholesale or establish runtime behavior. The changed test initializer explicitly supplies `EnableQueryCost`; written fixture intent remains distinct from passing tests.

## Rule queries use the configured server engine

In the selected non-agent server wiring, `rules.EngineQueryFunc` receives the same `queryEngine` whose options include `EnableQueryCost`. The reload callback applies configured limits only under that feature flag. Recording and alerting rules invoke the supplied query callback; its constructor passes nil options, so the selected engine defaults retain operator ceilings. A nonzero configured duration replaces the startup timeout; zero retains its fallback. This traces the standard caller path, not arbitrary injected callbacks, agent mode or observed rule execution. [H76/R01–R18]

## Remote enumeration and density sampling are different capabilities

The selected estimator opens the ordinary queryable for series counting independently of its optional `CostSamplingQueryable`. Configured remote readers make the selected fanout refuse density sampling, while ordinary enumeration still has a remote-client path. Required remote matchers can cause a particular selector to return without a client read. Without a sampler, positive-series selectors use the supplied global scrape interval and float cost `1.0` and add `errCostSamplingFallback`. However, `Annotations.Add` keys by `err.Error()`: repeated identical fallback additions deduplicate. Do not promise one separately identifiable returned warning per selector, actual network traffic or accurate histogram density. [H77/E01–E16]

## A raw deadline error need not become a typed timeout

The selected `contextErr` converts context errors at its call sites, but series expansion can return a raw iterator/context error that is wrapped with `expanding series`. Recovery preserves that wrapped error. `returnAPIError` recognizes `ErrQueryTimeout`, whereas a raw wrapped deadline without that type falls to execution classification. Default statuses therefore differ: timeout `503`, execution `422`; the optional `overrideErrorCode` can replace defaults. The selected `max_duration` rejection counter also requires the typed timeout and cost-duration cause. These are source paths, not observed HTTP responses or every endpoint/error case. [H78/T01–T12]

## Evaluator sample units differ from result count and physical I/O

Selected child evaluators share `queryBudget`. Float input charges one unit; histogram input uses `HPoint.size()`, whose selected formula is `(p.H.Size() + 8) / 16`. Materialized subquery consumption passes a negative step to avoid charging those selected input points again. With the budget enabled, the selected merge also attributes child work outside parent windows; a step-invariant child contributes reads once even when total-sample statistics repeat. These selected branches support evaluator input accounting, not bytes transferred, physical storage reads or exhaustive evaluator correctness. [H79/S01–S13]

## FAQ

### Can a larger HTTP timeout now bypass every server limit?

No. Parser acceptance differs from the selected engine/parent-context limits. The unchanged engine still constructs a bounded execution context; exact effective behavior requires the relevant configuration and engine implementation.

### Are timeout and max_query_duration interchangeable?

No. The after timeout parser drops the above-ceiling rejection while still requiring positivity. With the query-cost feature enabled, the cost override retains its ceiling semantics and gains an explicit negative-value API rejection; with the feature disabled, the selected option extractor ignores cost overrides. Do not silently apply one parameter’s policy to the other.

### Does every failed estimate leave a successful query with a warning?

No. Warning conversion happens after successful execution. Request cancellation or timeout can still fail the execution, and the error-return path does not call the pending comparison’s finish method.

### Do the API and engine now share one identical timestamp?

That is not established. The API samples its start before construction; the engine records its own deadline during construction. The explicit earlier-start calculation constrains estimation, but exact equality and actual stop timing were not verified.

### Can an unchanged engine justify retaining every lifecycle paragraph?

No. The API caller changes the order and error-routing context around that engine. Retained callee text and modified caller explanations require separate decisions, with source provenance bound to the actual target revision.

### Were existing tests or documentation accepted wholesale?

No. Test declarations were inspected without execution. Six initial clause groups and four bounded follow-up subtopics were assessed with explicit limits; full-page acceptance remains unestablished. This note is same-agent source review, not independent or owner acceptance.

### Does an Add call per selector imply distinct returned warnings?

No. The same fallback error string is used as a map key, so duplicate additions collapse. The positive-series guard also matters; a zero-series selector does not enter that fallback branch. [H77/E02, E03, E15]

### Does every rule implementation use the inspected limits?

That is not established. The source trace covers the standard non-agent server wiring and enabled cost feature, not arbitrary injected query callbacks. [H76/R01–R18]

### Is every duration error an HTTP 503 timeout?

No. Typed timeout and raw wrapped expansion errors can follow different classifications, and an optional callback can override default status codes. No response was measured. [H78/T01–T12]

### Does samplesRead measure bytes downloaded from remote storage?

No such claim follows. The selected counters charge evaluator input units and relative histogram size, with explicit child-result reuse handling; physical I/O is outside this observation. [H79/S01–S13]

## Read-only reproduction and source references

An equivalent pinned Git diff was inspected. This command displays source changes only; it does not run an API, tests, storage or an estimator.

```sh
git -c core.fsmonitor=false diff --no-ext-diff --no-renames 5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4 80cd8d97bdfce88014a652d15723559d00a15902 -- web/api/v1/api.go
```

[S1: after API.queryTimeout](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L919-L932)

[S2: after queryConstructionError](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L940-L951)

[S3: after API.estimateQueryCost](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1002-L1022)

[S4: after API.queryCostCeilings](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L877-L889)

[S5: after API.estimateForComparison](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L966-L969)

[S6: after pendingCostComparison.finish](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L975-L997)

[S7: after API.costRequested](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L847-L860)

[S8: after returnAPIError](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1371-L1399)

[S9: after API.query](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L625-L729)

[S10: after API.queryRange](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api.go#L1201-L1331)

[S11: after query.executionContext](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L397-L406)

[S12: after Engine.newQuery](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L877-L953)

[S13: after resolveDurationLimit](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L990-L1002)

[S14: after Engine.Close](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/promql/engine.go#L744-L753)

[S15: before API.queryTimeout](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L919-L939)

[S16: before queryConstructionError](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L945-L950)

[S17: before API.estimateQueryCost](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L983-L1003)

[S18: before API.queryCostCeilings](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L872-L884)

[S19: before API.costComparison](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L957-L979)

[S20: before API.costRequested](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L842-L855)

[S21: before returnAPIError](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L1351-L1379)

[S22: before API.query](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L624-L727)

[S23: before API.queryRange](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api.go#L1182-L1311)

[S24: before func testEngine(](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api_test.go#L72-L91)

[S25: before func newQueryCostTestAPI(](https://github.com/prometheus/prometheus/blob/5ccc8ab7aa5f19a3a7f667c7fc4923a2af2095b4/web/api/v1/api_test.go#L5196-L5221)

[S26: after func newQueryCostTestAPI(](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api_test.go#L5219-L5252)

[S27: after func TestQueryCostEstimationQueueTimeout(](https://github.com/prometheus/prometheus/blob/80cd8d97bdfce88014a652d15723559d00a15902/web/api/v1/api_test.go#L6116-L6160)

[R1: Go context deadline contract](https://pkg.go.dev/context#WithDeadline). Current primary API contract, not a Prometheus runtime observation.

The complete root Apache-2.0 license and file notices are retained. All campaign artifacts remain restricted internal review material, without blanket file-level, training or public-publication clearance.
