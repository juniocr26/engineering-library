# Does the selected facade use the same synchronization strategy in both cuts?

The newer `func._cache` supplies `Condition()`. With the owned storable result, a same-key waiter reused the first result and one computation occurred; the earlier facade computed twice. This does not establish global exactly-once execution or performance.
