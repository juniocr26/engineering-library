# Prometheus Builder: adding, replacing and recording deletion

Status: source-reviewed experimental correction written by Codex. Human approval is pending. This chapter is not a model-generated answer, training gold, a published manual, or evidence that model weights improved.

The source is Prometheus revision `b2a602494b65bda38316eabaef7e0d834a6814dd`, file `model/labels/labels_common.go`. The bounded contract consists of `Builder.Set` and `Builder.Del`. The original local-agent responses and the independently frozen evaluation criteria are preserved in the private continuation workspace. The caller-only answer was refused; the answer supplied with both methods passed structural checks but omitted the helper and return behavior. This correction addresses those omissions directly.

## Set chooses a branch from the value

The method takes a name and a value, both strings, and returns a builder pointer. Its first condition is `v == ""`. That condition concerns the value, not whether the name is empty, whether the builder has no labels, or whether a label already exists. On that branch the implementation immediately executes `return b.Del(n)`. It therefore delegates to the deletion helper and returns the helper's result. The later search and append statements are not reached on this branch.

For a nonempty value, the method iterates over `b.add`. Each iteration compares `a.Name == n`. At the first matching entry, it assigns `b.add[i].Value = v` and executes `return b`. The collection being searched is the pending additions slice. Saying only “updates an existing label” loses that distinction and can suggest that the method directly scans or rewrites the base collection.

If the search finishes without a match, the method assigns `b.add = append(b.add, Label{Name: n, Value: v})`, then executes `return b`. The new element uses the supplied name and value. The method does not sort the additions in this body. Both nonempty-value paths return the same receiver expression; the empty-value path returns the result of the helper call.

## Del records deletion and adjusts pending additions

The helper accepts `ns ...string`. It visits the supplied names in order. For each name, it ranges over `b.add` and checks `a.Name == n`. At a match, the written slice update is `b.add = append(b.add[:i], b.add[i+1:]...)`. After that inner scan, it executes `b.del = append(b.del, n)`. Once the outer loop finishes, it executes `return b`.

Recording a requested deletion is not conditional on finding an addition. A name can therefore be appended to the deletion slice even when the inner search finds no matching pending addition. There is no deduplication check before that append. Passing the same requested name repeatedly is not shown to be normalized into a single deletion marker. Conversely, a call with no requested names does not enter the outer loop and reaches the return.

These observations describe the written loops and updates. They do not establish behavior for arbitrarily malformed internal slices, prove normal completion for every possible receiver state, or establish concurrency safety. The selected code contains no locking or independent validation that would justify such guarantees.

## Why the helper changes what can be documented

With only the caller available, an author can identify the empty-value delegation, the search of additions, the replacement branch, the append branch and the written returns. The author's evidence does not include how the helper records deletions. Naming a helper is different from possessing its implementation.

With both methods available, the deletion slice update becomes directly inspectable. The explanation can now distinguish a deletion request from immediate modification of a base collection, explain the removal expression for pending additions, and identify the helper's return. Adding that source is useful only if the final explanation actually uses it correctly. In this experiment, the neural answer with the helper still cited only the caller and omitted the helper contract. The extra context therefore did not establish a complete factual improvement.

## Boundaries of this chapter

The selected methods do not assign to `b.base`. They also do not remove entries from `b.del` on the nonempty-value path. This chapter does not infer how another method later combines the base, additions and deletions. That requires its own source, including the relevant build variant. It also does not infer name validation, database operations, errors, execution timing, memory-allocation guarantees, or automatic synchronization from these two methods.

Preserving the return behavior matters even when prose about adding or replacing sounds plausible. The baseline mentioned a returned builder; the helper-context answer dropped that fact. An intervention must preserve correct existing facts as well as add missing ones. Structural writer acceptance, bilingual equivalence and successful source retrieval are separate checks from that complete-contract requirement.

## Source references and review

The exact selected excerpts, physical lines, source hash and producer identity are in `source-excerpts.json`. Upstream source is [labels_common.go at the frozen revision](https://github.com/prometheus/prometheus/blob/b2a602494b65bda38316eabaef7e0d834a6814dd/model/labels/labels_common.go). The source is under the Apache License 2.0; its original license is preserved privately with the snapshot. The source program was not executed for this review. EN/PT-BR code identifiers and conditions are checked separately from the neural responses, and neither language is approved for publication automatically.
