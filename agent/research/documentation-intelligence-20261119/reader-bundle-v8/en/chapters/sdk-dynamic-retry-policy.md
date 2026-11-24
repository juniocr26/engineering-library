# Dynamic retry policy: defaults, deadline guards and interval direction

Codex-authored source-reviewed correction, pending owner approval. Frozen Temporal SDK revision 7e0d845246d36fc7f62ade2af885554f94c29db9. Actual baselines: sdk-retry-function, sdk-retry-with-constants and sdk-contiguous-contract. Expanded evidence: [source excerpts](../references/ref-79609dc406795dd47c3d.md). No SDK application was compiled or executed.

The conditional builtin interpretation follows the [Go language definition](https://go.dev/ref/spec#Min_and_max).

## A policy is built before any retry is attempted

The function `createDynamicServiceRetryPolicy` receives ctx with the written type `context.Context` and returns `backoff.RetryPolicy`. Its body constructs and configures a policy object. It contains no operation callback, sleep, attempt loop or invocation of a retrier. A statement about eventual retry behavior therefore requires another consumer's code. The preserved local-agent baselines blurred configuration and execution, and one later answer misread both the interval arithmetic and the deadline guards.

This correction explicitly adds the policy constructor and setters from the same frozen SDK revision. That added evidence supports the configuration handoff, but it does not retroactively make an unsupported earlier model statement correct. The implementation remains source-reviewed documentation, not a measured execution of the SDK or a neural-weight improvement.

## The constants disagree with one source comment

The declared initial interval is `200 * time.Millisecond`. The declared default expiration interval is `60 * time.Second`, and the coefficient constant is 2. The nearby explanatory comment mentions 20ms, but the assignment used by the body refers to the declared 200-millisecond constant. A source comment can be useful context while still being inconsistent with the implementation. Copying the comment's smaller number loses the literal contract.

The function first assigns the expiration constant to `timeout`. It does not begin by deriving a duration from an unconditional context deadline. Initializing `timeout`, deciding whether to replace it and configuring the resulting policy are three separate steps. A complete account must retain the default path as well as the context-dependent path.

## The deadline branch is not a minimum with sixty seconds

The outer guard is `ctx != nil`. Inside it, the code samples now with `time.Now()`, then obtains expiration and ok from `ctx.Deadline()`. The replacement occurs only when `ok && expiration.After(now)`. That branch assigns `expiration.Sub(now)` to `timeout`. A missing deadline or a deadline that does not satisfy the strictly-future test leaves the initialized duration unchanged.

There is no comparison selecting the earlier of that future deadline and the sixty-second default. In the ordinary interpretation of the supplied time operations, a future deadline farther away than sixty seconds can therefore produce a longer configured duration. The source does not promise that every non-nil context implementation completes its Deadline call successfully. The guard is a written interface comparison, not proof that all typed-nil implementations or arbitrary methods are safe.

## Record the maximum expression without reversing its direction

The next assignments set `initialInterval` from the initial-interval constant and `maximumInterval` from `max(timeout/10, retryServiceOperationInitialInterval)`. The second operand is the same declared initial-interval constant. It is not a literal twenty milliseconds. Under Go's predeclared `max` binding, that expression chooses the larger operand: the initial interval acts as a floor on this computed configuration value, rather than a cap on `timeout/10`. With the ordinary duration interpretation, the default sixty seconds yields six seconds for this expression.

The word `max` is still an identifier whose binding matters. The earlier unfiltered census refused a binding conclusion because imported time sources included an ignored generator package. A later optional `go/build` experiment inspected all 157 immediate Go files in the SDK package and complete censuses for the three imported packages. Under explicit Darwin/arm64 and Linux/arm64 profiles, 78 ordinary SDK files are active; official build selection excludes the generator, while actual declared import names and package/local declarations leave the bare name lexically unshadowed. The [binding receipt](../references/ref-e655163bba280abaad01.md) and [source census](../references/ref-7d9703565731a2eee35a.md) preserve the proof. This supports the predeclared interpretation under those supplied complete censuses and a valid package build. It does not prove type checking or runtime behavior, and the production syntax parser and default agent routing remain unchanged.

## The setter sequence stores configuration

The body calls `backoff.NewExponentialRetryPolicy(initialInterval)`, then `SetBackoffCoefficient`, `SetMaximumInterval` and `SetExpirationInterval` in that order, and finally returns policy. The supplied constructor initializes an `ExponentialRetryPolicy` pointer using the argument and named defaults for other fields. The three supplied setters assign their respective arguments to fields and have no return result. Their bodies do not run the operation, clamp the provided duration or enforce a wall-clock deadline.

The outer coefficient argument comes from the constant 2, the maximum-interval argument is the computed expression and the expiration argument is `timeout`. Other constructor defaults are not a basis for invented numeric limits or attempt counts here. The source handoff explains what is configured while leaving later delay calculation, retry eligibility, cancellation and actual service activity to their own inspected consumers. The corrected EN/PT chapter remains pending owner approval and is not approved training gold.

## Engineer FAQ

<!-- reading-section: faq:initial-interval-comment-mismatch -->
### Is the configured initial interval 20 or 200 milliseconds?

The constant used by the body is 200 milliseconds. The nearby 20-millisecond comment disagrees with that declaration. The correction follows the written constant and preserves the discrepancy as review evidence.

<!-- reading-section: faq:future-deadline-not-sixty-second-cap -->
### Does a future deadline always shorten the sixty-second default?

Only a strictly future deadline replaces the default, and the shown assignment uses its remaining duration directly. It does not take the minimum with sixty seconds. Missing or nonfuture deadlines leave the default path unchanged, subject to normal completion of the supplied methods.

<!-- reading-section: faq:policy-configuration-not-retry-schedule -->
### Does creating the policy perform a retry or guarantee a sleep duration?

The constructor function configures and returns a policy. The supplied `ComputeNextDelay` consumer separately checks attempts and expiration, computes and clamps an interval and applies jitter. Actual operation invocation, sleeping and cancellation belong to further consumers. Neither the stored maximum nor the default calculation alone is an observed service retry schedule.

The optional build-filtered evidence now supports the maximum expression's lexical binding under two explicit profiles, conditional on complete source and valid compilation. It does not turn policy configuration into an observed retry schedule, a full module/type proof or owner approval.
