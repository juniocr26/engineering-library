# OpenCV: depth selection follows nested return conditions

This experimental chapter documents `coerceTypes` from the pinned OpenCV source recorded in the evidence. It corrects an actual local-agent response from the earlier campaign, without generating that rejected response again. Codex authored and source-reviewed the correction. Owner approval, training approval and publication remain absent. The complete selected function is small, but flattening its nested conditional expression changes the contract. The review therefore follows the expression's ordered return paths and retains the boundary between selecting a depth code and converting array elements.

## Equal depths end the decision immediately

The first condition is `depth1 == depth2`. If it is true, the expression returns `depth1`. No later branch is selected on this path. Calling this a maximum operation is unnecessary and obscures the direct equality case: the implementation does not call a maximum helper or compare unequal values here. The input flag does not override this first branch. Any explanation of the later promotion conditions must be conditional on the two input depths being unequal.

For unequal inputs, the next condition checks `((depth1 <= CV_32S) & (depth2 <= CV_32S)) != 0`. Both comparisons belong to the same enclosing branch. Their results are combined with bitwise conjunction, then compared with zero. This is not a logical short-circuit conjunction. The selected source supplies the symbolic boundary but does not supply its numeric definition or a complete inventory of valid depth codes. We therefore preserve the source expression instead of silently substituting assumed enum values or promising validation of arbitrary integers.

## The smaller-depth branch also depends on the operation flag

Inside that branch, the nested condition is `((int)!muldiv & (depth1 <= CV_8S) & (depth2 <= CV_8S)) != 0`. Only when this combined condition is true does the function choose `CV_16S`; otherwise it chooses `CV_32S`. The operation flag is a necessary part of the first result's condition, together with both smaller-depth comparisons and the enclosing unequal-depth branch. Saying that both inputs below the earlier boundary always select the latter result loses a real subcase. Moving the smaller-depth comparisons outside their enclosing branch creates a different decision tree.

The spelling of the flag suggests multiplication and division, and the source contract supplied to the original baseline asks about that distinction. The body itself only evaluates the Boolean flag; it does not inspect an operation identifier or perform multiplication or division. This correction describes the explicit flag-dependent selection without adding a catalog of callers or guaranteeing how every arithmetic operation supplies that flag. Such a claim would require reviewing those call sites separately.

## The remaining unequal-depth path uses element size

When the earlier combined depth-bound condition is false, the final branch checks `((CV_ELEM_SIZE1(depth1) > 4) | (CV_ELEM_SIZE1(depth2) > 4)) != 0`. It chooses `CV_64F` when that expression is true and `CV_32F` otherwise. The comparison is strictly greater than four, and the operator combining comparison results is bitwise disjunction. The macro definition is outside the selected unit. Its expansion, any validation behavior and its behavior on invalid depth inputs are therefore not inferred here. The expression supplies the branch condition, not permission to invent missing macro semantics.

## What is returned, and what the baseline got wrong

The function returns an integer depth code. It does not receive arrays, write output elements or perform the conversions represented by that code. The historical response put the smaller-depth test outside its actual parent branch, omitted the negated operation flag, and described a return rule that contradicted the nested smaller-result case. The correction restores the complete branch order in both languages. Original response bytes, source identity, exact quotation and the historical review are retained for comparison. This source-reviewed candidate is not a new independent transfer example or evidence that model weights improved.
