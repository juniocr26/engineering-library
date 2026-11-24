# Historical V1 cut — superseded

The unamended action references in this V1 cut are retained for diagnostic history. Use the [corrected V2 manifest](v2/manifest.json) for current owner review. No row in either version is approved for training.

# Candidate datasets under review

These files contain source-reviewed candidates, explicit development references
and preserved model diagnostics. **No row is approved for training or publication.**
No ordinary agent or trainer automatically loads this directory.

| Artifact | Records | Meaning |
|---|---:|---|
| chapter-deltas.jsonl | 50 | EN/PT before/after versions of 24 reviewed historical pairs and one new owned adapter pair |
| faq-candidates.jsonl | 154 | Two language rows for each of 77 reviewed question/answer pairs |
| lifecycle-development-references.jsonl | 24 | Paired source-change scenarios with proposed, corrected development action references |
| model-diagnostics.jsonl | 42 | Actual local model requests and their output/review lineage, including failures |
| structural-helper-references.jsonl | 9 | Six complete lexical quotes and three safe refusals from actual standard-library source |

The categories overlap. FAQ rows derive from chapters, EN/PT rows form pairs,
and the historical chapter revisions are versions of existing research, not
24 new independent source families. Do not sum these counts into a claim of
unique training examples.

Chapter enrichment is not automatically a source-evolution label. Most source
revisions stayed fixed while their documentation gained FAQs, clearer context
or a specific correction. Those rows explicitly have no source-evolution
classifier target. This prevents teaching that a source-preserving refactor
always requires full documentation regeneration.

Model outputs are diagnostics, not corrected assistant targets. Action agreement
alone does not approve the explanation or its Portuguese translation. The
preserved critical false removal and malformed translations must not become
positive training targets.

All owned synthetic variations share one conservative source family. Revisions,
language pairs, helper/caller variants and overlapping source evidence must stay
together. Go and CPython standard-library contracts retain their common ancestry.
No automatic family split or independent holdout is certified here.

The [manifest](manifest.json) pins each JSONL file and identifies counts, lineage
and remaining review requirements. The [license inventory](../source-license-provenance.json)
preserves source provenance without granting training rights. Question-specific
claim/span alignment, owner review, confidentiality/licensing review and all
training-readiness gates remain necessary. Current approved training rows,
optimizer steps and trained adapters are all zero.
