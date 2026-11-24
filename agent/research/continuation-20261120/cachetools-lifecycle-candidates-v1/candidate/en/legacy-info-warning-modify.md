# Is the legacy fourth positional boolean still warning-free?

The current `cached` recognizes the boolean in the new fourth slot as legacy statistics configuration, clears its condition value and emits `DeprecationWarning`. The owned explicit-warning-filter observation retained statistics; the boolean did not become condition-based synchronization.
