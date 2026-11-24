# ReadFrom bookkeeping after the pinned revision

This isolated maintenance candidate describes `middleware.httpFancyWriter.ReadFrom` in `go-chi/chi` at `9f8adb1aabaa8a91180a821111d3f8e668d1c0bf`. Its preceding revision is `04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9`. The revision changes the non-tee, non-discard branch; this is a source-level description, not a passing runtime test.

When `f.basicWriter.tee != nil || f.basicWriter.discard`, the method still calls `io.Copy(&f.basicWriter, r)` and returns its pair immediately. That branch does not reach the subsequent direct `ReaderFrom` path. Evidence: `middleware/wrap_writer.go:211–220` in both pinned revisions.

Previously, the direct path asserted `ResponseWriter.(io.ReaderFrom)`, called `f.basicWriter.maybeWriteHeader()`, and then called `rf.ReadFrom(r)`. It accumulated `int(n)` and returned `n, err`. Evidence: old `middleware/wrap_writer.go:221–225`.

The revised direct path calls `rf.ReadFrom(r)` first. If that call returns normally, the written guard `n > 0 && !f.basicWriter.wroteHeader` conditionally assigns `http.StatusOK` to the wrapper's `code` and sets `wroteHeader = true`. The guard does not test `err == nil`. It then adds `int(n)` to `bytes` and returns `n, err`. Evidence: new `middleware/wrap_writer.go:221–228`.

The removed `maybeWriteHeader()` call previously reached `WriteHeader(http.StatusOK)` when `wroteHeader` was false. In contrast, the new block contains assignments to wrapper fields rather than a direct `WriteHeader` call. `Status()` returns `code`, and `BytesWritten()` returns `bytes`. Evidence: new `middleware/wrap_writer.go:117–120,130–135` and old `:117–120`.

## FAQ

**Does this mean every ReadFrom reports StatusOK?** No. The revised bookkeeping block requires both `n > 0` and a false `wroteHeader` after the delegate returns. Existing wrapper state and the early branch matter.

**Is positive n proof of a nil error?** No. The shown guard does not inspect `err`; the returned pair is preserved.

**Does the revision run the same path for Tee or Discard?** No. The preceding branch uses `io.Copy` and returns early. This candidate does not certify the runtime behavior of `io.Copy`, the writer, or the network.

**What was actually verified?** Exact read-only Git snapshots, the real revision diff, the receiver declaration through the bundled Go syntax parser, and the stated source order. No external test suite, Go typecheck, HTTP server or network write was executed.

This is a manually reviewed source-maintenance candidate, not owner approval, training gold, a general verifier or an independent holdout result.
