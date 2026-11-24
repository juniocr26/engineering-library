# Does the selected facade use the same synchronization strategy in both cuts?

The selected `func._cache` supplies `RLock()` and the owned same-key calls computed twice.
