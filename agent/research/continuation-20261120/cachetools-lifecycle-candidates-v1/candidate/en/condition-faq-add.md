# What does the newly available `condition` argument coordinate?

With a standard condition and a cache that stores the result, the selected wrapper tracks pending keys and lets a same-key waiter reuse the stored result. The owned different-key computation progressed separately. This is bounded in-process coordination, not a distributed exactly-once guarantee.
