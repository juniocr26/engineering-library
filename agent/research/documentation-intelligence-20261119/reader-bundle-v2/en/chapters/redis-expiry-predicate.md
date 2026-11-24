# Redis: the exact boundary of the expiry predicate

This experimental chapter describes `checkAlreadyExpired` at the frozen source revision recorded in the accompanying evidence. It corrects an actual local-agent baseline preserved from the earlier campaign. The correction was authored and source-reviewed by Codex; it is pending owner approval and is neither published documentation nor approved training data. Redis was not executed for this review. The selected function answers a bounded question about an expiry timestamp and server state, so the distinction between its return value and operations performed elsewhere is central.

## The current-client guard comes first

The first executable statement tests `server.current_client` and then its flags against `CLIENT_MASTER`. The outer condition uses logical conjunction, which protects the client-field access when there is no current client. The flag expression is a bitwise membership test. When that combined condition is true, the function returns `0` immediately. The later time comparison is not reached on this path. This guard concerns the current client's flags; replacing it with a vague claim that the server is in a particular master mode loses the actual ownership and condition.

If the guard does not return, the function evaluates `when <= commandTimeSnapshot() && !server.loading && !server.masterhost`. The comparison includes equality: a timestamp equal to the helper's result satisfies the first operand. A strictly earlier timestamp also satisfies it. The function can return true through this expression only when the comparison succeeds and both subsequent negated server fields are true. A timestamp alone therefore does not determine the result. Either server condition can prevent the expression from becoming true.

## Evaluation order and helper uncertainty

Logical conjunction short-circuits. Once this second statement is reached, the time comparison is evaluated first. A false comparison skips both later operands; a false loading-state operand skips the final operand. The original supplied function called `commandTimeSnapshot()` without showing its implementation; this campaign adds that helper separately below. From that original excerpt alone, no clock implementation, unit, caching policy, thread behavior or wall-clock freshness was established. The added helper below identifies a stored snapshot and its documented millisecond type; update timing and runtime clock guarantees still require separate evidence. The explicit comparison and branch order remain directly inspectable.

The return type is an integer, while the final logical expression supplies a truth value under C's expression rules. The early integer `0` and the false final expression both produce a false result, but they arise from different control paths. The former avoids the time-helper call altogether. A source-grounded explanation should preserve this difference when discussing evaluation, instrumentation or a future controlled test. The original selected predicate did not establish caller behavior; the additional caller excerpt below now separates its mutation branches from the predicate result.

## Comment rationale and actual operations

The source comment discusses past expiration timestamps, loading an append-only file, replication context, and waiting for an explicit delete from the master. It provides rationale for the guard and state conditions. The function body itself does not insert a key, delete a key, propagate a command, set an expiry or wait for a network message. Turning that rationale into a promise that this function performs those operations was a critical error in the historical baseline. The corrected contract describes the predicate and leaves the surrounding database workflow outside the selected evidence.

## Comparison and review status

The baseline broadly recognized an expiry check but omitted the current-client early return and blurred server roles. It also dropped the exact comparison and final state guard while presenting comment rationale as behavior. This correction restores those conditions without claiming that the local model learned them. Both language versions preserve the same technical expressions and boundaries. Exact source hashes, physical citation lines, original response, historical caller identity and review findings remain available in the accompanying artifacts; these integrity checks support review but do not substitute for owner approval.

## Engineer FAQ and actual caller responsibility

<!-- reading-section: faq:predicate-versus-key-deletion -->
### Does the predicate itself delete an already-expired key?

Its body returns a decision. The separately inspected caller tests that decision, then invokes `dbGenericDelete` on the true branch, updates dirty state, rewrites the client command and issues notifications and a reply. The false branch invokes `setExpire` and its own update/notification sequence. Those are caller operations, not hidden operations performed by the predicate.

<!-- reading-section: faq:inclusive-expiry-boundary -->
### Is an equal timestamp considered past the boundary?

The written comparison includes equality, but only after the current-client early-return guard has not fired. The loading and masterhost conditions still participate in the final conjunction. Time comparison alone is insufficient.

<!-- reading-section: faq:clock-snapshot-value -->
### What time value does the inspected getter provide?

The additional implementation directly returns `server.cmd_time_snapshot`; its declaration uses the millisecond time type. It does not read a fresh clock in that body. The exact update schedule, all callers, clock reliability and concurrent access remain outside this bounded review.

These added source excerpts resolve the named getter and one actual caller without turning comments about replication or AOF loading into operations inside the predicate. No Redis command, server, key mutation or replication workflow was executed.
