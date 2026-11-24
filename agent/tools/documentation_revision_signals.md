# Written Python revision signals

`documentation_revision_signals.observe_revision` version 0.1.1 compares two
explicit source snapshots in memory. It returns structural observations and
always leaves `documentation_action` null. It does not choose ADD, MODIFY,
REMOVE or NO-OP, edit documents, call a model or change ordinary Ruby routing.

Each source card has exactly `revision`, `path`, `source` and `sha256`. The caller
supplies the complete UTF-8 source text and its digest. The path is a provenance
label; the API does not open it or establish current filesystem state. Hashes
and revision strings are not authenticated repository provenance or permission.

Up to eight unique lexical function/method selectors are supported. A trusted
Python worker parses each supplied module, including Python type comments, and
compares AST dumps without ordinary location attributes. Function fingerprints
come from the original module AST, preserving multiline string values. The
existing retrieval ownership checks establish a complete physical declaration
or an explicit unknown. Decorators, imports and inspected source are never run.

The module signal is `IDENTICAL_WRITTEN_MODULE_AST` or
`DIFFERENT_WRITTEN_MODULE_AST`. Each selector has an identical/different written
declaration signal or `DECLARATION_COMPARISON_UNESTABLISHED`. A missing,
conditional, duplicated or otherwise ambiguous declaration never proves feature
retirement. A newly found declaration does not establish a documentation need.

If a selected declaration is unchanged but the enclosing module AST changed,
`unchanged_selection_requires_dependency_review` is true. This deliberately
includes unrelated additions: no dependency resolver proves they are irrelevant.
An identical module AST also does not establish external dependency or runtime
equivalence. Ordinary comments and formatting can affect documentation without
changing these ASTs. Type-ignore locations can conservatively change a module
fingerprint. Fingerprints are tied to the Python/runtime and implementation
identity and are not a portable semantic identity across grammar versions.

Limits are 65,536 bytes per source, 8,192 AST nodes per module, eight selectors,
6,144 bytes per full quotation and 24,576 combined quotation bytes. The worker
has a three-second deadline and a 131,072-byte response bound. The parent checks
closed response shapes, signal consistency and physical quotations without
parsing inspected ASTs after the deadline. This is a bounded trusted producer,
not a sandbox against arbitrary code in its own process. Malformed, unsupported,
oversized or timed-out input yields `INCONCLUSIVE` without observations.

Caller containers are copied per operation; later caller mutation does not
rebind the frozen transport. Implementation and shared retrieval/workspace
hashes are rechecked before delivery. No persistent cache or journal is created.

The first real-revision study uses already inspected cachetools revisions. It
matched five manually frozen structural references, while the existing restricted
lifecycle planner safely returned INCONCLUSIVE for all five complete external
modules. Manual documentation proposals are kept separate from those refusals.
This is development evidence, not independent holdout, semantic completeness,
owner approval or training gold. The initial 0.1.0 study and exact source are
preserved separately from the type-comment-aware 0.1.1 cut.
