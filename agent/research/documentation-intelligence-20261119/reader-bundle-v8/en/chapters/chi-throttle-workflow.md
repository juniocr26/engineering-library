# Throttling: admission budgets, waiting and deferred release

Codex-authored source-reviewed correction; pending owner approval.

chi revision c64ed7d6635f33a8b2feaff7dcfa55677023ac7d; middleware/throttle.go. Actual local-agent baseline: chi-throttle-workflow. [Exact source evidence](../references/ref-fe7353b4cadf7acc814c.md).

## Construction validates two different ranges

The actual local-agent baseline said the processing limit must be greater than zero, which matches the first guard. It also said the backlog limit must be positive. That second statement follows the panic message rather than the condition: the written guard is `opts.BacklogLimit < 0`. Zero is allowed by this guard. This is a critical boundary error repeated in English and Portuguese, despite the response citing both selected evidence IDs.

The selected function first panics when `opts.Limit < 1`, then panics on a negative backlog limit. It copies the configured status and substitutes `http.StatusTooManyRequests` only when that status is zero. The shown checks do not validate every conceivable capacity, duration or integer-overflow condition. A caller cannot infer complete configuration validation merely from the two explicit panic branches.

## Two channel budgets are shared by the returned middleware

The local throttler has a processing-token channel with capacity `opts.Limit` and a backlog-token channel with capacity `opts.Limit+opts.BacklogLimit`. The initialization loop fills the processing channel for the first limit entries and fills the backlog channel for the whole combined count. These channels have different jobs: admission consumes a backlog token, while invoking the next handler additionally requires a processing token.

The outer function returns `func(next http.Handler) http.Handler`. Applying that returned function produces `http.HandlerFunc(fn)`; it does not itself execute a request. The captured throttler and its channels belong to this constructed middleware instance. The selected implementation contains no user identifier or per-user rate bucket. Its waiting timer must not be confused with a fixed request allowance per time window.

## Admission, immediate processing and the waiting path

The request callback obtains `r.Context()` and enters an outer select. Its context-done case calls the retry-header helper with true, then calls `http.Error` with the cancellation text and configured status. Its default case calls the helper with false and reports capacity exceeded. Acquiring a backlog token instead registers a deferred send that returns that token when the callback's deferred work runs.

After admission, an inner select first tries to receive a processing token without waiting. On success, it registers a deferred processing-token return, calls `next.ServeHTTP(w, r)` and returns. This path does not create the later timer. If that immediate receive is unavailable, the default branch proceeds to `time.NewTimer(t.backlogTimeout)` and a separate waiting select.

The waiting select distinguishes timer expiry, context completion and a processing-token receive. Timer expiry reports a timeout with false passed to the header helper. Context completion explicitly stops the timer and reports cancellation with true. Receiving a processing token schedules a defer that stops the timer and returns the processing token, then calls the next handler. The backlog-token defer remains part of the surrounding callback's exit path.

## Deferred release does not interrupt the next handler

The processing-token send is written inside a deferred function, while the next-handler invocation is a direct synchronous call. Describing the token as returned before the handler runs reverses the shown order. Both cleanup calls are registered before the next-handler call. On its ordinary return, the later-registered processing cleanup runs before the earlier-registered backlog cleanup as the surrounding callback returns. This is a source-level account of scheduling the cleanup, not a measurement of concurrent request completion.

The timer governs waiting for a processing token. The shown timer-select code is no longer running alongside the next handler after that token has been acquired. It therefore does not establish forced interruption of a blocked handler. Likewise, if multiple select cases are ready, this source does not establish a deterministic preference for cancellation over admission. The code contains cancellation branches, not a universal guarantee that every already-cancelled request is rejected before any handler call.

## The retry-header helper has its own conditional contract

The helper first returns when the configured retry callback is nil. Otherwise it calls that callback with the supplied context-done Boolean. It divides the returned duration by `time.Second`, clamps a negative duration to zero seconds and increments a nonnegative result when a fractional second remains. It then sets `Retry-After` using a decimal string. Exact positive whole seconds are not increased by the remainder branch.

These operations describe the helper when its calls complete normally; they do not prove that an arbitrary configured callback cannot panic or block. The chapter expands the baseline's useful header observations into the surrounding admission and release workflow, and corrects the zero-backlog boundary. The additional option and state-field excerpts were read for this correction, rather than being falsely attributed to the model's original selected context. This source-reviewed bilingual candidate is pending owner approval and has not been published or promoted to training gold.

## Configuration at the actual entry point

The wrappers and the options constructor do not have identical default behavior. The full frozen file shows that `Throttle` explicitly supplies a 60-second backlog timeout. `ThrottleBacklog` forwards its duration argument. `ThrottleWithOpts` copies `opts.BacklogTimeout` directly; this function does not replace zero with that wrapper default.

| Option | Source-backed rule in ThrottleWithOpts |
| --- | --- |
| Limit | Values below 1 panic before channel creation. |
| BacklogLimit | Negative values panic; zero passes this guard. |
| BacklogTimeout | Copied directly; no positivity guard is shown. |
| StatusCode | Zero becomes the too-many-requests constant; another value is copied. |
| RetryAfterFn | Nil skips the retry-header helper body; another value is called on rejection paths. |

## Engineer FAQ

<!-- reading-section: faq:concurrency-not-per-user-rate -->
### Is this a per-user request-rate limit?

The captured channels limit concurrent admission and processing for the middleware instance. There is no per-user identifier, map of user buckets or periodic refill in this selected implementation. The timer limits waiting for a processing token.

<!-- reading-section: faq:zero-backlog -->
### Does zero backlog disable all requests?

No. With a valid positive limit, the backlog-token capacity is the sum of that limit and zero. Zero backlog passes the explicit validation guard; admission and processing tokens still have separate roles.

<!-- reading-section: faq:retry-header-not-execution -->
### Does setting RetryAfterFn automatically retry a request?

The helper sets `Retry-After` when its callback completes normally. It does not invoke the next handler again or implement client retry. Negative delays become zero; a positive fractional second is rounded up, while an exact whole second is preserved.

The language ordering and ready-case limits follow the [Go defer rules](https://go.dev/ref/spec#Defer_statements) and [select rules](https://go.dev/ref/spec#Select_statements), rechecked during this review. No upstream middleware was executed.
