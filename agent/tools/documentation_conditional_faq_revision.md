# Conditional FAQ record revisions

`documentation_conditional_faq_revision.plan_revision` version 0.1.0 optionally
recommends ADD, MODIFY, NO-OP or INCONCLUSIVE for the exact paired record emitted
by `documentation_closed_faq` 0.1.0. It uses two trusted
`ClosedDependencyObserver` 0.1.2 instances for previous/current registered source
snapshots. It never recommends REMOVE, edits files, calls a model or changes
ordinary Ruby routing.

The supported question kind is `conditional-static-integer-return-v1`. Every
proposed answer retains the unverified runtime-name-binding caveat. A helper-only
change can modify its integer answer even when the entry source is unchanged.
Different source evidence with the same integer can retain the exact existing
record. These decisions concern this conditional question, not arbitrary source
behavior or a complete chapter.

The caller declares a complete inventory for one canonical question, explicit
managed ownership and absence of a human-content conflict. The existing record
is either None with no expected hash, or exactly the paired
`{language: {question, answer}}` shape, bounded to 16,384 canonical UTF-8 bytes,
with its expected SHA-256. The input is copied before observations. Existing
records must equal either the current or previous trusted rendering. Free prose,
asymmetric language edits, missing caveats and unregistered existing questions
are preserved with INCONCLUSIVE, not silently adopted or overwritten.

An absent question can produce ADD under the declared complete owned inventory.
This does not imply that a new software feature was introduced. Both previous
and current source profiles must still be admitted. Missing modules, removed
symbols, conditional definitions, unsupported calls or ambiguous bindings remain
INCONCLUSIVE. The tool cannot establish retirement.

Both observer configurations and physical registered files are rechecked after
candidate construction. Loaded implementation identities are checked before and
after. Facts and new candidate text are withheld on failed rechecks. Each
observer has its existing at-most-three-second parsing worker; the wrapper also
checks an eight-second elapsed delivery limit. That is not a hard cancellation
guarantee for operating-system file I/O or an atomic snapshot across roots.

NO-OP retains the structured record, without document-byte or mtime claims. A
changing result carries the prior record as memory history and canonical hashes.
It is a recommendation only: a separate approved document application must bind
full document bytes, preserve complete history and check current source again.
No publication, owner approval, training gold or automatic trainer ingestion
follows from these results. The API is trusted local process code, not a sandbox
against arbitrary Python access or authenticated repository provenance.
