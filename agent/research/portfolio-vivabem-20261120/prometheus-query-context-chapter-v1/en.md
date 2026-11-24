# Prometheus: query construction, cancellation and cleanup lifetimes

`prometheus/prometheus` · `b2a602494b65bda38316eabaef7e0d834a6814dd`

CANDIDATE_FOR_SOURCE_REVIEW · not owner-approved, not Gold, not training data.

## Scope and verification

This chapter follows the selected Prometheus revision through PromQL query construction, execution, cancellation, reader cleanup and HTTP result finalization. The repository is development-exposed; its earlier sixteen builder/bookkeeping records are a different evaluation scope. This is manual source-first documentation, with no model generation, actual query, database, storage startup, upstream suite or Go compilation. Thirty-three complete declarations were extracted by the integrity-verified native Go syntax tool; the source cards below are separately selected source spans, including parts of larger functions. Neither kind of quote proves runtime behavior.

## Query interfaces separate responsibilities

`QueryEngine` declares instant and range constructors returning `Query` and an error. `Query` separately declares `Exec`, `Close`, `Cancel`, `Statement`, `Stats` and `String`. The concrete `query` stores a queryable, parsed statement, statistics, result matrix, cancellation function and engine reference. The interface comment says execution can occur only once; the inspected forwarding `Exec` body is not an observed one-time enforcement guard. No reuse or concurrent-access guarantee follows from this inspection.

[S1](#s1) [S2](#s2)

## Construction precedes evaluation

Both public constructors first call `newQuery`, then enter the active-query queue, parse and validate the expression, and preprocess it into the evaluation statement. The instant path uses the same start/end time and zero interval. The range path additionally rejects expression types other than scalar or instant vector. These selected paths do not call the query’s `Exec`; they also are not established as pure functions, because parser, options, tracking and wrapping collaborators may have effects. Construction can fail before a query is returned.

[S4](#s4) [S5](#s5) [S6](#s6)

## Per-query state and optional cost policy

`newQuery` supplies default options when absent, chooses lookback and start-timestamp policy, and creates statement/statistics state. Optional native-histogram conversion wraps the queryable. When query-cost enforcement is enabled, it reads operator ceilings and optional per-query overrides, resolves effective limits, and records a construction-time deadline. Without that feature, these selected cost-limit fields are not populated by this block. This is not a complete specification of every feature or storage wrapper.

[S6](#s6)

## A zero request inherits the ceiling

`resolveUintLimit` returns the ceiling when the requested value is zero. Otherwise, a zero ceiling or a request no greater than the ceiling admits the request; an excessive request returns `ErrLimitAboveCeiling`, rather than silently clamping it. Thus request zero does not necessarily disable a finite limit. `resolveDurationLimit` uses analogous comparisons with nonpositive durations. In the duration setup, a positive configured duration ceiling can replace the startup timeout ceiling; a generic statement that every duration override only lowers the startup timeout would be wrong.

[S6](#s6) [S7](#s7)

## Execution creates its own cancellation context

`executionContext` uses the engine timeout when the query has no stored deadline; otherwise it uses the stored deadline and an explicit cause, selecting the query-cost cause when the effective maximum duration is positive. With cost enforcement, constructors use and cancel a local context while retaining the absolute deadline in query state. Later, `Engine.exec` creates an execution context, assigns its cancel function to the query and defers cancellation. This preserves a deadline boundary in the source; it does not measure cancellation latency or establish immediate interruption of arbitrary collaborators.

[S3](#s3) [S4](#s4) [S5](#s5) [S8](#s8)

## Cancel is a signal, not buffer cleanup

`query.Cancel` invokes the stored cancellation function only when it is non-nil. The selected query constructors do not initialize that function; assignment occurs in `Engine.exec`. The inspected cancellation test expects a pre-execution cancellation to have no effect, using a synthetic test statement. This source path does not show cancellation waiting for the query to stop, releasing result slices, or making unsynchronized concurrent use safe.

[S2](#s2) [S6](#s6) [S8](#s8) [S15](#s15) [S16](#s16)

## Queue admission has a separate release function

`queueActive` returns a no-op release function when no tracker exists. Otherwise it calls the tracker’s `Insert`; on success it returns a closure calling `Delete` with the returned index. Constructors and execution defer the release after successful admission. A selected no-op branch is not proof of a global concurrency limit, and the source does not establish that an arbitrary tracker cannot block or fail. Queue cleanup is distinct from result-buffer cleanup.

[S4](#s4) [S5](#s5) [S9](#s9) [S10](#s10)

## Execution forwards values, errors and warnings

`query.Exec` delegates to the engine and builds a `Result` with independent error, value and warning fields. `Engine.exec` records metrics and timers, admits the query, checks its context and dispatches an evaluation statement or a test statement. Unsupported statement types reach an explicit panic in this selected function. The wrapper does not promise every failure is an error-free value or that warnings disappear on error. `Result` accessors reject an existing error before checking the requested value type.

[S2](#s2) [S8](#s8) [S9](#s9) [S23](#s23)

## The storage reader has a distinct lifetime

`execEvalStmt` computes time bounds and asks the queryable for a `Querier`. A returned error exits before installing its close defer; after successful acquisition it defers `querier.Close()` and evaluates with that reader. The selected deferred call does not explicitly propagate a returned close error. The storage interface includes `Close() error` through `LabelQuerier`. This reader cleanup is not the later `query.Close` operation over result slices; arbitrary storage-provider behavior was not executed or certified.

[S11](#s11) [S21](#s21) [S22](#s22)

## Result ownership can survive a late error

The instant evaluation path stores a matrix before converting it to a vector/scalar or returning a matrix. A string result returns earlier without that matrix assignment. The range path stores its matrix before a later context check and sorting. Consequently an error returned after that assignment does not prove the query holds no result buffers. The selected code and HTTP caller maintain cleanup separately from success. These paths do not prove that every error leaves allocated buffers or that every returned value is an independent deep copy.

[S12](#s12) [S19](#s19) [S20](#s20)

## Close returns point slices to pools

`query.Close` loops over its stored matrix and passes float and histogram point slices to the corresponding pool helpers. Those helpers ignore nil slices and otherwise return a zero-length view to a pool. The selected body does not call `Cancel`, wait for execution, close a storage reader, clear the matrix or guard against repeated calls. Therefore this chapter does not promise idempotence, immediate operating-system memory release, safe result reuse after closing or concurrent safety.

[S2](#s2) [S13](#s13)

## HTTP finalization follows result handling

The selected instant/range handlers install a deferred fallback after successful query construction: close the query if the named result has no finalizer. Normal execution-error and success returns instead carry `qry.Close` as the result finalizer. The registered wrapper defers that finalizer before calling the response/error handling path. Thus the handlers do not simply close every query before returning its value to their caller. The fallback also covers unwinding without an assigned finalizer; it does not prove recovery from every panic or that every collaborator completes. No HTTP request was made.

[S17](#s17) [S18](#s18) [S19](#s19) [S20](#s20)

## HTTP validation is not an engine-wide theorem

The HTTP range handler checks end before start, a nonpositive step and a resolution quotient greater than 11,000 before constructing a query. These are selected API-layer guards; do not silently attribute all of them to `Engine.NewRangeQuery`. Likewise, finalizers follow this registered HTTP wrapper’s contract, not every possible direct `QueryEngine` consumer. No global range-validity, request-limit or external caller guarantee is claimed.

[S5](#s5) [S18](#s18) [S20](#s20)

## Engine shutdown is a third close operation

`Engine.Close` returns nil for a nil engine; otherwise it closes the active-query tracker if present, returning that error, or returns nil without a tracker. Its comment requires callers to ensure the engine is no longer in use. The selected body is not a loop cancelling all live queries, freeing each query matrix or closing each storage reader. It does not establish safe shutdown while queries are active or that the query logger is closed by this method.

[S14](#s14) [S25](#s25)

## Error recovery and tests have explicit limits

`evaluator.Eval` defers a recovery handler that converts selected panic values into its returned error/warnings state. That scope does not extend automatically to construction, every engine statement branch, response handling or the recovery handler’s own collaborators. The inspected timeout/cancellation tests use `NewTestQuery`, which injects a `parser.TestStmt`; the cancellation test synchronizes channels and separately checks cancellation before starting. These test bodies were inspected and syntax-parsed, not run, and are not evidence of real storage cancellation latency or passing integration tests.

[S15](#s15) [S16](#s16) [S24](#s24)

## FAQ

### Are Cancel and Close equivalent?

No. `Cancel` calls an installed cancellation function; `Close` returns stored matrix slices to pools. Neither selected body supplies the other operation, and signalling cancellation is not an observed wait for completion.

[S2](#s2) [S13](#s13)

### Does canceling before execution permanently cancel a new query?

Not in the selected construction/cancellation path. The cancellation field starts unset and is assigned by engine execution; the inspected synthetic test expects pre-execution cancellation to have no effect. This is not a concurrent timing guarantee for every caller.

[S2](#s2) [S6](#s6) [S8](#s8) [S16](#s16)

### Does a zero requested cost limit disable a finite operator limit?

No. `resolveUintLimit` returns the operator ceiling for a zero request. A positive request above a finite ceiling produces an error rather than a silent clamp. The selected per-query cost policy is gated by the query-cost feature.

[S6](#s6) [S7](#s7)

### Can an errored query still require result cleanup?

Yes, the source allows that: the range path assigns its matrix before a later context error check. The HTTP execution-error result still carries the close finalizer. This does not say every failure allocates buffers or establish a runtime leak.

[S12](#s12) [S19](#s19) [S20](#s20)

### Must the HTTP query handler close before returning its result?

The selected normal success/error paths transfer `qry.Close` as a finalizer, and the registered wrapper defers it around response handling. The handler’s fallback closes only when its named result has no finalizer. Replacing this with unconditional early cleanup would discard that ownership distinction; no such code change was made.

[S17](#s17) [S18](#s18) [S19](#s19) [S20](#s20)

### Does Engine.Close guarantee that all live work has stopped?

No such guarantee is established. It closes the active tracker when present and requires an engine no longer in use. Per-query cancellation, pooled result cleanup and reader cleanup are separate responsibilities.

[S2](#s2) [S11](#s11) [S14](#s14)

## Read-only reproduction example

Equivalent pinned Git source retrieval was executed during acquisition. From the public Prometheus checkout, this command displays source only; it does not start a service, evaluate PromQL or access storage. Native parser observations are syntax-only and are separately archived with raw requests, responses and producer identity.

```sh
git -c core.fsmonitor=false show b2a602494b65bda38316eabaef7e0d834a6814dd:promql/engine.go
```

## Source references, rights and limits

<a id="s1"></a> [S1: promql/engine.go:165–196](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L165-L196)

<a id="s2"></a> [S2: promql/engine.go:313–393](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L313-L393)

<a id="s3"></a> [S3: promql/engine.go:397–434](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L397-L434)

<a id="s4"></a> [S4: promql/engine.go:788–831](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L788-L831)

<a id="s5"></a> [S5: promql/engine.go:835–881](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L835-L881)

<a id="s6"></a> [S6: promql/engine.go:886–968](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L886-L968)

<a id="s7"></a> [S7: promql/engine.go:976–1017](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L976-L1017)

<a id="s8"></a> [S8: promql/engine.go:1091–1146](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1091-L1146)

<a id="s9"></a> [S9: promql/engine.go:1148–1183](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1148-L1183)

<a id="s10"></a> [S10: promql/engine.go:1208–1219](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1208-L1219)

<a id="s11"></a> [S11: promql/engine.go:1257–1315](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1257-L1315)

<a id="s12"></a> [S12: promql/engine.go:1315–1397](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1315-L1397)

<a id="s13"></a> [S13: promql/engine.go:3438–3462](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L3438-L3462)

<a id="s14"></a> [S14: promql/engine.go:750–762](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L750-L762)

<a id="s15"></a> [S15: promql/engine.go:1075–1085](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1075-L1085)

<a id="s16"></a> [S16: promql/engine_test.go:159–226](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine_test.go#L159-L226)

<a id="s17"></a> [S17: web/api/v1/api.go:214–221](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L214-L221)

<a id="s18"></a> [S18: web/api/v1/api.go:443–465](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L443-L465)

<a id="s19"></a> [S19: web/api/v1/api.go:625–729](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L625-L729)

<a id="s20"></a> [S20: web/api/v1/api.go:1201–1331](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/web/api/v1/api.go#L1201-L1331)

<a id="s21"></a> [S21: storage/interface.go:109–139](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/storage/interface.go#L109-L139)

<a id="s22"></a> [S22: storage/interface.go:191–206](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/storage/interface.go#L191-L206)

<a id="s23"></a> [S23: promql/value.go:365–409](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/value.go#L365-L409)

<a id="s24"></a> [S24: promql/engine.go:1754–1787](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine.go#L1754-L1787)

<a id="s25"></a> [S25: promql/engine_test.go:5552–5573](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/promql/engine_test.go#L5552-L5573)

The full root Apache-2.0 license and original file notices are retained with the source packet. This is not blanket file-level, training or public-publication clearance. Campaign artifacts remain restricted internal review material. No current private Viva Bem data or source was used as model input.
