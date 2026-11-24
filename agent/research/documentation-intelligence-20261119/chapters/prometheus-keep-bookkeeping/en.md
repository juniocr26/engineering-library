# `Builder.Keep`: inclusion, callback returns and deletion bookkeeping

Codex-authored source-reviewed correction; pending owner approval.

Prometheus revision b2a602494b65bda38316eabaef7e0d834a6814dd; actual preserved baseline: prometheus-keep-bookkeeping. [Exact source excerpt](source-excerpts.json).

## Names to keep, not a namespace collection

The selected declaration is `func (b *Builder) Keep(ns ...string) *Builder`. The receiver is a builder pointer, and `ns` is a variadic string parameter. The local-agent baseline invented a namespace collection and reversed the filter direction. Its useful observation that the method updates deletion bookkeeping does not rescue those errors. The original response remains preserved as a rejected diagnostic.

The callback tests `slices.Contains(ns, l.Name)`. A name included in that supplied list takes the callback's early return. A name not included reaches the append to `b.del`. Describing this as deleting the supplied names reverses the shown predicate. The identifier `ns` is an abbreviation in a parameter name, not evidence that this API manages namespace objects or a namespace registry.

## The callback return does not return from `Keep`

`Keep` calls `b.base.Range` with a function taking one `Label`. The return inside that function has no result expression. It finishes that callback invocation for a visited label whose name is included. It is not the outer method's pointer return and does not by itself show that the complete `Range` traversal stops after the first included label.

After the `Range` call completes normally, the method reaches `return b`. That returns the same receiver pointer written in the method, rather than a newly allocated builder, a list of filtered labels or a Boolean. The selected body has no explicit nil-receiver guard. Successful completion of `Range` and the operations inside its callback must not be silently converted into a guarantee about every possible runtime input.

## Bookkeeping is narrower than deleting stored labels

For each visited name that fails the inclusion test, the written operation is `b.del = append(b.del, l.Name)`. It appends to the existing deletion slice. The body does not clear that slice before traversal, deduplicate the appended names or undo an earlier deletion marker when the current inclusion test succeeds. A matching name merely avoids this invocation's append path.

The selected method contains no assignment to `b.add` or `b.base`. It does not directly rewrite the base collection or filter pending additions in the shown body. Some older queue wording incorrectly described additions filtering; that premise must be corrected before future experiments use it as an expected answer. Final materialization of a builder is a separate contract requiring its own source evidence.

## Useful boundary cases and their evidence limits

Under the ordinary behavior of the imported `slices.Contains` operation, an empty supplied name list does not contain any visited name, so each visited name reaches the deletion-bookkeeping append. Repeating a name in the supplied list does not create an additional callback invocation in this body. These are source-derived consequences of the written test and callback, not observed executions of Prometheus.

The excerpt does not establish `Range`'s internal iteration order, thread safety, asymptotic cost or the contents of a later materialized label set. The correction therefore says “visited base names” and “deletion bookkeeping” rather than claiming an executed global deletion. It reuses a completed local-agent baseline from the previous campaign, with no repeated inference. English and Portuguese preserve the same predicate, receiver, callback boundary and final result. The chapter remains a source-reviewed candidate pending owner approval, with retained license and notice files and no automatic training or publication authorization.

## Engineer FAQ

<!-- reading-section: faq:keep-does-not-restore-deletion -->
### Can Keep restore a name already marked for deletion?

For an included visited name, the callback returns without appending a new deletion marker. It does not remove an old marker from `b.del`. Preserving an inclusion test and undoing prior bookkeeping are different operations.

<!-- reading-section: faq:keep-addition-preservation -->
### Will Keep remove an addition that was not in the supplied name list?

The selected method visits the base and does not assign `b.add`. It cannot be documented as filtering pending additions from this body. The separately inspected `Builder.Range` visits pending additions after processing base labels against its copied state.

<!-- reading-section: faq:callback-return-scope -->
### Why does an early return not stop the outer method?

The return is inside the callback passed to the base traversal. After that traversal completes normally, the outer `Keep` still reaches `return b`. Callback completion, traversal completion and the outer pointer return must remain distinct in both languages.

The additional `Builder.Get` source also shows why bookkeeping alone is not a complete result description: it checks pending additions before deletion markers and then the base getter. These consumer observations do not select a package build variant or execute Prometheus.
