# Contextual notifications: persistence, Redis and delivery

Patterns generalized from private source reviewed on 2026-11-12. Keys, entities and examples below are conceptual, not installation contracts. [Index](../index.md) · [Identity](../security/personal-identification.md).

## Responsibilities and events

An appointment transition changes business state; a durable effect records notification intent; Redis maintains a queryable inbox; an event channel updates open interfaces; a queue forwards push to the provider. Success at one stage does not prove the others. Delivery recovery must not reschedule appointments, repeat purchases or cancel again.

Reviewed events include approved scheduling, time-change requests/proposals, confirmation, cancellation and session entry/start. A proposal should communicate pending acceptance; confirmation should state the new time; cancellation should retain the original time reference. One person's entry and room availability for another need distinct text.

Recipients come from appointment participants. Name/CRP belong to that appointment's professional; patients do not acquire CRP in the message because their account is also professional. Photos prioritize the counterpart's profile in the appointment role, falling back to account photo and then avatar. Contextual selection does not modify the global image. Persisted relative path, public-disk root, symlink and URL are separate layers: concatenating/removing segments without checking them breaks photos. Private physical layout remains internal.

## Canonical Redis model

A per-user ordered index references individual content hashes. A separate string stores versioned dispatch evidence. Conceptual example:

```text
product:inbox:synthetic-user -> sorted set of IDs
product:item:synthetic-event -> content and read-state hash
product:dispatch:synthetic-event -> state, owner and deadline
```

These names are synthetic. Current behavior reads only the canonical index; legacy-index reads are removed. One representation reduces divergence between listing, deletion and recovery. Connection prefix and domain namespace are separate layers to check when a key appears missing.

A Lua write combines hash, index, expiry and dispatch evidence in one Redis operation. It does not include SQL commit, broker or provider. Inspected implementation uses a default 30-day retention. The index orders by temporal score with a small random perturbation, preserved on update: exact chronological order of nearby events is not guaranteed.

Reads use reverse order and offset pages; references without hashes are removed and can leave short pages. Concurrent inserts can shift offsets: do not promise snapshots or absolute freedom from duplicates. Content timestamps take precedence, falling back to scores for incomplete records. Missing fields receive defaults without old structures.

Marking read changes the hash and renews its TTL without changing index score/TTL. Renewed content does not guarantee the list reference remains. Message updates can preserve read state without dispatching again. Read, expired, removed and delivered-to-provider are distinct states.

## Identity, leases and recovery

Stable IDs should derive from recipient, entity and event to avoid repeating the same bell. Distinct events need distinct discriminators. Idempotent insertion checks existence without rewriting state; this does not mean every application producer uses stable identity.

Evidence created before commit waits for confirmation before becoming dispatch-eligible. Owner/deadline reservations prevent concurrency. Compare-and-set prevents an old worker from overwriting a new owner. Attempts/backoff are bounded and preserve TTL. Uncertain queue acceptance requires retaining owner identity because the job may have arrived despite the publisher losing the response.

Recovery searches only eligible evidence and requires the item to remain in both index and hash. It does not recreate business events. SCAN avoids blocking KEYS operations, but locating a small batch can still traverse a large namespace. Constant cost is not guaranteed. Ambiguous old evidence or waiting-for-commit state does not authorize automatic replay.

SQL rollback can leave Redis evidence waiting for commit until expiry, a cross-system boundary limitation. Completed job state proves neither visible delivery nor user reading. Retrying after uncertain external results prevents promising exactly-once device delivery.

## Drawer, Web, Android and iOS

The drawer retrieves persisted history and displays read state, text and photos; live events accelerate updates without replacing authoritative reads. FCM uses active registrations and an asynchronous queue. Normal/critical push have different priorities/TTLs; critical entry/start messages can preserve context. Not all critical text is anonymous. Reviewed producers exclude CPF without a universal arbitrary-text filter.

Web can use contextual photos only for allowed events and same-origin HTTPS URLs under an authorized path; badge remains application-wide. Fallback uses a generic icon. The observed native Android contract is data-only without that photo: rendering belongs to the client. Server-side APNs payload does not establish a native iOS app.

Permissions, iOS web-app installation, Focus/Do Not Disturb and power restrictions affect presentation. These need device/production-environment validation; this review certifies no platforms. FCM acceptance does not guarantee sound, heads-up or display.

## Verification and troubleshooting

Inspected existing tests cover role/event text, CPF exclusion, photos, Redis reconstruction, pagination/orphans and simulated HTTP transport. They were not run during this update. Redis/HTTP mocks establish neither real servers, credentials, workers, accessible images nor OS presentation.

Investigate boundaries in order: committed transition, durable effect, persisted item, live publication, queue acceptance, provider response and device. Preserve uncertain-outcome state; do not delete locks or replay business operations to recover alerts. Sessions, presence, cache and operational history can also use Redis, with separate connection/retention contracts.
