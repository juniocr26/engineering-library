# Does moving the helper require changing every lock-scope statement?

On a miss, the selected lock-only memoization wrapper calls the user function outside its cache lock. The owned two-thread case computed twice and returned the cache-winning value to both callers.
