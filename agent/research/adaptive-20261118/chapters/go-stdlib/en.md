# Go comparison, zero values and slice searches

Experimental correction chapter authored by Codex after static source review. Human factual and bilingual approval is pending. This is neither unchanged model output nor approved training data. No source program was executed.

Source provider: cached Go 1.27.4 Linux ARM64 image `golang@sha256:0a5f7fe796599ff487605987432e7619ae45beeb2fba4c2ce0b907879932aebf`. No Git revision is inferred. Exact source bytes, ranges and SHA-256 values: [source-excerpts.json](source-excerpts.json). License: [BSD-style Go license](source/LICENSE).

## Comparison and floating-point exceptions

`Less[T Ordered](x, y T) bool` returns `(isNaN(x) && !isNaN(y)) || x < y`. Its written expression treats a detected NaN on the left as less only when the right is not NaN; two detected NaNs do not satisfy that first term. This behavior is different from simply returning `x < y`.

Source unit: `Less`, `cmp/cmp.go:28-30`. [Exact quotation](source-excerpts.json).

`Compare[T Ordered](x, y T) int` computes `xNaN` and `yNaN` first. When `xNaN` is true, it returns `0` if `yNaN` is also true and `-1` otherwise. When only `yNaN` is true, it returns `+1`. These branches precede the ordinary `x < y` and `x > y` comparisons.

Source unit: `Compare`, `cmp/cmp.go:40-59`. [Exact quotation](source-excerpts.json).

The remaining `Compare` branches return `-1` for `x < y`, `+1` for `x > y`, then `0`. The quoted `isNaN[T Ordered](x T) bool` helper returns `x != x`; its source comment says this is false for non-floating types. No distinction between signed NaN categories is written in these functions.

Source unit: `isNaN`, `cmp/cmp.go:63-65`. [Exact quotation](source-excerpts.json).

## Variadic zero-value selection

`Or[T comparable](vals ...T) T` declares `var zero T`, visits `vals` in order and returns the first `val` for which `val != zero`. Finishing the loop returns `zero`. An empty argument sequence therefore reaches that final return without entering the loop.

Source unit: `Or`, `cmp/cmp.go:69-77`. [Exact quotation](source-excerpts.json).

The `Or` signature uses the `comparable` constraint and variadic `...T`; it does not use `Ordered`, a two-argument signature or an unrestricted `any` constraint. Its comparison is with the zero value of `T`, not a universal null-only predicate. The body does not sort the values.

Source unit: `Or`, `cmp/cmp.go:69-77`. [Exact quotation](source-excerpts.json).

## Binary search returns position and membership

`BinarySearch[S ~[]E, E cmp.Ordered](x S, target E) (int, bool)` declares two results. Its source comment requires the slice to be sorted in increasing order. The body initializes `n := len(x)` and `i, j := 0, n`; it does not sort the input before searching.

Source unit: `BinarySearch`, `slices/sort.go:126-143`. [Exact quotation](source-excerpts.json).

While `i < j`, `BinarySearch` computes `h := int(uint(i+j) >> 1)`. If `cmp.Less(x[h], target)` is true, it assigns `i = h + 1`; otherwise it assigns `j = h`. The returned index is `i`, not a forced `len(x)` for every absent target.

Source unit: `BinarySearch`, `slices/sort.go:126-143`. [Exact quotation](source-excerpts.json).

The final boolean is `i < n && (x[i] == target || (isNaN(x[i]) && isNaN(target)))`. It checks both the index bound and equality or the paired NaN condition. On an empty slice, the loop is skipped and the result is `0, false`. The `cmp.Less` and `isNaN` helper sources must be considered when explaining their special cases.

Source unit: `BinarySearch`, `slices/sort.go:126-143`. [Exact quotation](source-excerpts.json).

## Minimum by comparator is a scan

`MinFunc[S ~[]E, E any](x S, cmp func(a, b E) int) E` checks `len(x) < 1` and calls `panic("slices.MinFunc: empty list")` on that branch. Otherwise it initializes `m := x[0]` and scans indices starting at `1`. Its signature returns one `E`, not an index and boolean.

Source unit: `MinFunc`, `slices/sort.go:79-90`. [Exact quotation](source-excerpts.json).

For each remaining element, `MinFunc` assigns `m = x[i]` only when `cmp(x[i], m) < 0`. A comparator result of `0` leaves the current `m` unchanged; the source comment describes choosing the first minimal element. The body writes its local accumulator and contains no slice-element assignment or sorting call. Comparator side effects and ordering consistency remain external assumptions.

Source unit: `MinFunc`, `slices/sort.go:79-90`. [Exact quotation](source-excerpts.json).

## Scope and use

These are bounded source contracts. Generic type validity, compiler behavior, callback purity and runtime performance were not established by executing these files. The chapter is retained for owner review and is not loaded automatically into model prompts or any trainer.
