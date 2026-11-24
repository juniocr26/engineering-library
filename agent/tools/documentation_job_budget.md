# Durable helper job budget

`HelperJobBudget` and `JobBoundRetrieval` are optional local research APIs. They
address a specific limitation: constructing a new `HelperRetrieval` instance
resets its per-instance counters. The coordinator reserves from one surviving
operator-owned job journal before calling that existing helper. Ordinary Ruby
requests and direct helper callers are unchanged.

The operator supplies an existing canonical journal directory and a closed
configuration containing `job_id`, `registry_sha256`, `max_steps`,
`max_quote_bytes` and `deadline_utc`. The registry hash must exactly match the
helper's frozen source registry. Job and helper journals must be separate from
each other and from all registered source roots. The configuration also binds
the loaded coordinator and workspace implementation hashes. Changed or legacy
configuration requires explicit review; no migration is attempted.

Each accepted request reserves one step and 6,144 quote bytes before dispatch.
Unused quote allowance is deliberately not refunded. A job permits at most 16
steps and 98,304 reserved quote bytes. A smaller quote allowance can prevent a
step even if the eventual quotation would have been short. This conservative
reservation makes budget safety independent of an unknown worker outcome.

Reservations and completions are exclusive files. The shared directory is pinned
by device and inode; local nonblocking POSIX process locking coordinates separate
instances and processes. A busy journal refuses the operation without retry.
Strict schemas, request hashes, reservation chaining and implementation identity
detect malformed or inconsistent surviving records. File and parent-directory
fsync precede successful delivery.

A repeated request ID with the same payload returns `DUPLICATE_COMPLETED` and
references its previous audit record without source quotations. A pending record
returns `UNKNOWN_COMPLETION`, consuming its original reservation without replay.
A different payload under that ID refuses. New independent requests may use the
remaining allowance. An exception or uncertain helper result does not release
the reservation or grant permission to repeat the call.

The deadline is checked at reservation and immediately before dispatch. A worker
already running can finish later. The late completion is recorded as
`LATE_COMPLETION_REVIEW_REQUIRED`, and its quotation is suppressed. If completion
auditing fails, the coordinator likewise suppresses the helper result and retains
the reservation. This is not remote cancellation or a hard real-time guarantee.

`COMPLETED` means the helper call was audited, not that a fact is established.
Inspect `helper_result.status` and the evidence limitations separately; a helper
refusal is also a completed call. No wrapper outcome approves publication,
commits, document edits or training.

The journal must remain under trusted operator ownership. Hashes are not
signatures and cannot detect a consistent rollback of the whole directory.
Clock rollback is detected relative to surviving timestamps; the OS clock is
still trusted. This is neither a distributed lock nor a verified Windows
implementation. It bounds helper calls and quote reservations, not model tokens,
total job filesystem time, general tool effects or bypassing callers. No server,
plugin, automatic route or model-selected planner is installed.

The development demonstrations cover four reconstructed instances, interrupted
completion, a virtual-clock late result, an injected audit-write failure and six
concurrent processes. At most two reservations and two helper dispatches were
admitted under the shared two-step allowance. These synthetic controls establish
local budget behavior, not independent model quality or throughput improvement.
See `helper-job-budget-evaluation.json` in the dated research directory.
