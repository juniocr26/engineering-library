# TTL replies: sentinels, time basis and units

Codex-authored correction reviewed against pinned source; pending owner approval.

Repository: redis; revision: 1a9eb051aa243f9d0e5a8a8afa6c4801bf52a9fb; baseline: redis-ttl-replies. [Exact source excerpts](../references/ref-2fa45784e58806458d3e.md).

## A reply is not a C return value

The selected declaration is `void ttlGenericCommand(client *c, int output_ms, int output_abs)`. Its C result type is void. Calls to `addReplyLongLong` send the values selected by this body through the client reply mechanism. The actual local-agent baseline confused those replies with C return values and described an adjustment by five hundred seconds. Both errors appeared in English and Portuguese. This correction separates control flow, the time basis and the output unit.

No Redis server was started for this chapter, and no command was sent over the network. The account follows the frozen source and its four immediate wrappers. The original selected packet did not include key lookup, expiration storage or the command-time snapshot implementation. This review adds the snapshot helper below while preserving the other dependency boundaries.

## Missing keys leave before expiry conversion

The local ttl starts at -1. The body looks up `c->argv[1]` with `LOOKUP_NOTOUCH`. If the resulting pointer is `NULL`, it calls `addReplyLongLong(c,-2)` and executes a bare return. That path does not proceed to the expiry lookup or the final unit selection. The selected code therefore distinguishes a missing key from an existing key without an expiry.

For an existing key, `kvobjGetExpire` supplies expire. When expire equals -1, the conditional body is skipped and ttl remains its initial sentinel. The later sentinel branch replies with -1 directly. It does not apply the millisecond-to-second arithmetic to that sentinel. Claiming every reply goes through division would erase this separate branch.

## The two flags answer different questions

For an expiry other than the sentinel, `output_abs` selects expire itself or `expire-commandTimeSnapshot()`. The first is the stored absolute expiry representation; the second subtracts the command snapshot to form a relative quantity. The body then clamps a negative computed ttl to zero. This clamp occurs before the final reply selection and is not the missing-key or no-expiry sentinel.

The other flag, `output_ms`, chooses between ttl and `((ttl+500)/1000)`. The added 500 belongs to the millisecond quantity before integer division by 1000; it is not five hundred seconds added after conversion. For a nonnegative quantity within the arithmetic's representable range, the expression rounds using that offset. This chapter does not claim overflow protection or a universal clock guarantee, because neither is established by the selected body.

## The wrappers fix the flag combinations

The four adjacent wrappers make the combinations explicit. `ttlCommand` passes (0, 0); `pttlCommand` passes (1, 0); `expiretimeCommand` passes (0, 1); `pexpiretimeCommand` passes (1, 1). Reading those calls links relative versus absolute output and seconds versus milliseconds without guessing from the generic function's name. Each wrapper delegates; these bodies do not establish the internals of reply serialization.

The useful baseline observation about missing and non-expiring keys is preserved. The corrected contract adds early exit, the sentinel bypass, the independent flags and the zero clamp. This is a documentary correction against pinned source, not a new inference or proof of model learning. License notices, the original wrong response and review status remain separate, with no automatic approval for training or publication.

## Wrapper combinations

| Wrapper | output_ms | output_abs | Non-sentinel time basis and unit |
| --- | --- | --- | --- |
| ttlCommand | 0 | 0 | Relative quantity converted to seconds |
| pttlCommand | 1 | 0 | Relative quantity in milliseconds |
| expiretimeCommand | 0 | 1 | Absolute expiry converted to seconds |
| pexpiretimeCommand | 1 | 1 | Absolute expiry in milliseconds |

The missing-key and no-expiry sentinels follow their separate branches rather than this conversion table.

## Engineer FAQ

<!-- reading-section: faq:sentinels-before-rounding -->
### Are -2 and -1 rounded or divided by 1000?

No. The missing-key path replies with -2 and returns before expiry conversion. The no-expiry path replies with -1 through its own sentinel branch. Neither goes through the ordinary non-sentinel arithmetic.

<!-- reading-section: faq:clock-snapshot-refresh -->
### Does commandTimeSnapshot read a fresh clock on each call?

The added helper implementation directly returns `server.cmd_time_snapshot`. The header declares the millisecond time type and describes this field as the root-execution snapshot. The getter itself contains no clock syscall; full update timing and runtime clock guarantees require their own evidence.

<!-- reading-section: faq:reply-versus-key-deletion -->
### Does a successful TTL reply delete the key?

The selected generic body performs lookup, expiry selection and reply calls. It contains no explicit delete operation. Lookup-helper side effects and the client's actual wire delivery are not established by this excerpt, so this is not a global no-side-effect guarantee.
