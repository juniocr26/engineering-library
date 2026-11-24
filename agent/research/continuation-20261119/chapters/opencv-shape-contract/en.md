# Trailing shape compatibility includes channels

Codex-authored correction reviewed against pinned source; pending owner approval.

Repository: opencv; revision: 5d0660acfed08650cafec4876b4792a369a20601; baseline: opencv-shape-contract. [Exact source excerpts](source-excerpts.json).

## The baseline and the boundary

The actual local-agent response identified right-to-left comparison and the rule allowing a dimension of one. Those observations were useful, but incomplete. It omitted the added channel entries, the incremented dimension counts and the loop's stopping condition. In Portuguese, translating broadcasting as ordinary transmission also obscured the array-shape concept. This chapter keeps broadcasting as a technical term and describes the selected helper rather than an entire arithmetic operation.

The declaration is `static bool shapesBroadcastCompat(InputArray a, int acn, InputArray b, int bcn)`. It returns a Boolean compatibility decision. This is not evidence that it allocates the broadcast output, copies image data, chooses a numeric type or performs an arithmetic operation. Those would require separate caller and helper evidence.

## Channels join the compared shape

Two local integer arrays have room for `MatShape::MAX_DIMS + 1` entries. The calls `a.sizend(asz)` and `b.sizend(bsz)` supply the initial dimension counts and arrays used by this body. The next statements are `asz[ad++] = acn` and `bsz[bd++] = bcn`. Each writes the supplied channel count after the existing dimension entries, then increases its count.

Consequently, the first pair visited by the reverse loop is the appended channel pair. A description restricted to spatial dimensions loses an actual input to the decision. The source does not show a separate channel-equality guard: the channel entries pass through the same mismatch rule as the remaining visited entries. This observation does not establish every valid input range of `InputArray` or the implementation of `sizend`.

## A conjunction controls rejection and traversal

The indexes begin at `ad - 1` and `bd - 1`. Each iteration decrements both, and the loop continues only while both remain nonnegative. A visited pair rejects compatibility only when its entries differ and neither entry equals one. Equality therefore continues; an unequal pair containing one also continues. There is no branch that returns true immediately upon seeing a one: later visited pairs can still reject.

For conceptual dimension lists [2, 3] with four channels and [3] with four channels, the visited entries are the equal channel counts and the equal trailing spatial entries. The unmatched leading two is not visited by this loop. This is a source-derived trace, not an executed OpenCV test. It illustrates why saying every dimension must be compared would overstate the selected body.

## What the final return establishes

If no visited pair takes the rejection branch, execution reaches `return true`. Exhausting either index is enough to finish the loop. That fact is narrower than a general proof about every broadcasting rule elsewhere in OpenCV. The helper checks this trailing alignment and the supplied channel entries under its own input assumptions.

No performance benchmark was run. Nearby descriptions of this check as cheap cannot establish constant time or a measured speedup. The chapter corrects the preserved model response through source review; it does not demonstrate a changed model, a trained adapter or independent held-out transfer. The exact source and baseline identities remain attached, and the bilingual correction is still pending owner review.

