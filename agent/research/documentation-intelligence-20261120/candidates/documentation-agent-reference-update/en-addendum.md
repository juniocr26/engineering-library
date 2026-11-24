
## Source-reference maintenance supplement — 2026-11-20

The preceding current-cut statements describe the preserved previous campaign. This separate research supplement observes planner `0.3.6` and workspace maintenance `0.1.5`; it does not replace the earlier receipts, count old tests again or imply that the ordinary Ruby writer acquired these optional tools.

The planner accepts only a canonical, bounded repository-relative identity in the source-link path fields. Empty paths, `.` or `..` segments, absolute paths and unsupported characters require review. If both language claims already name the declared current path, it recommends `NO-OP`; a positively identified previous path that differs from the current path can recommend `MODIFY`. This is still an operator-declared source/claim protocol, not proof that an arbitrary path exists in a Git revision.

The filesystem preparation layer adds an independent identity check: supplied `current_path` and `previous_path` metadata must match the operation's registered current and previous files. Equal inline source bytes cannot certify a different path. The new guard rejects a false current-path `NO-OP` and a false previous-path relocation before candidate writes. A valid relocation still prepares an isolated EN/PT candidate; an already-current reference preserves the original bytes and metadata without creating a candidate root.

The twelve planner controls improved from 9/12 to 12/12, and the four physical-identity controls from 2/4 to 4/4, in development only. The frozen public Boltons evaluation remains 0/8 exact actions with eight abstentions; the old matrix remains 22/24. These are separate denominators. No permanent test files, active documentation, publication permissions or model weights changed.
