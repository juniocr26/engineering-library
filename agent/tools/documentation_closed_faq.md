# Conditional closed-source FAQ pair

`documentation_closed_faq.prepare_closed_return_pair` version 0.1.0 renders one
mechanical English/Portuguese question pair from a fresh
`ClosedDependencyObserver` version 0.1.2 observation. It supports only the
`conditional-static-integer-return-v1` question kind. It does not generate
general architecture explanations or choose a documentation lifecycle action.

The operator supplies an existing observer, a stable question ID and the exact
entry module and symbol. Arbitrary persisted JSON is not accepted as an observer.
Fresh observation rechecks the pinned registry, source bytes and producer code.
An admitted result retains the requested entry identity, integer value and the
explicit condition that runtime name bindings remain unverified in both languages.

The returned value stays in memory. It includes the source observation, evidence
key, observation hash and bilingual text hash. The text hash is not a feature
identity, source authorization or approval token. Compare the question ID and
kind separately. Formatting may change evidence while leaving pair text equal;
a helper-only value change updates the answer.

Missing, unsupported, stale or conflicting evidence returns `INCONCLUSIVE` with
no FAQ pair. It never recommends removal, writes documents, invokes a model or
authorizes publication or training. A caller must still review a proposed pair
and apply any document change through the existing ownership and preservation
controls.

The development evaluation has fourteen fixtures: eight conditional pairs and
six safe inconclusive results. All 23 fixture source files stayed unchanged.
These eight pairs are diagnostic controls, separate from the 77 chapter FAQ
pairs. See the [evaluation](../research/documentation-intelligence-20261119/closed-return-faq-evaluation.json)
and [clarified protocol](../research/documentation-intelligence-20261119/closed-return-faq-protocol-v2.json).
