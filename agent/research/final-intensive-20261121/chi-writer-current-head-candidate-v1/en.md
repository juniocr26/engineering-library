# Chi response wrappers: capabilities and shared accounting

Source-scoped development candidate, not owner approved. Revision `c64ed7d6635f33a8b2feaff7dcfa55677023ac7d`, `middleware/wrap_writer.go` and `middleware/wrap_writer_test.go`. Source was read and parsed; the Chi program and tests were not executed. This chapter describes the selected written implementation, not complete server behavior.

## Selection and architecture

`NewWrapResponseWriter` starts with `basicWriter{ResponseWriter: w}` and checks `http.Flusher`. When `protoMajor == 2`, both flushing and `http.Pusher` select `http2FancyWriter`. Other protocol values enter the branch checking `http.Hijacker` and `io.ReaderFrom`: all three capabilities select `httpFancyWriter`; flushing plus hijacking select `flushHijackWriter`; hijacking alone selects `hijackWriter`. The final fallback selects `flushWriter` when flushing exists, otherwise the base wrapper. This is the literal dispatch, not proof that every network protocol value is valid. [S1]

Each selected wrapper embeds base state. `WrapResponseWriter` declares status, bytes, tee, unwrap and discard operations in addition to `http.ResponseWriter`; it does not declare `ReadFrom`. Therefore callers must not infer that every returned wrapper supports `io.ReaderFrom`. The comment above `http2FancyWriter` mentions that interface, but the selected file declares its `Flush` and `Push` methods and no `ReadFrom` method for that receiver. No repository-wide absence or full Go method-set/type-check proof is claimed. [S1,S2,S6]

## State and write contracts

`Status()` returns `b.code`; `BytesWritten()` returns `b.bytes`. These are wrapper counters, not independent observations of delivery to a client. In discard mode the implementation still counts consumed writes, as the written test explicitly expects. `Tee(w)` replaces the single tee target; `Unwrap()` returns the original writer; `Discard()` sets the discard flag. The interface comment prohibits modifying the tee writer concurrently with writes; no synchronization guarantee is established here. [S2,S4,T2]

`WriteHeader` treats codes from 100 through 199 except `http.StatusSwitchingProtocols` as an informational branch: it delegates only when not discarding and does not assign the final-state fields there. Otherwise, only the first call while `!b.wroteHeader` assigns the code and flag, delegating only when not discarding. `maybeWriteHeader()` calls `WriteHeader(http.StatusOK)` when the flag is false. `flush()` invokes that helper before conditionally delegating `Flush`; discard suppresses the underlying flush call. [S3]

`Write` first calls that helper. In normal mode it writes to the underlying response, then sends only `buf[:n]` to the tee, if set. An underlying write error takes precedence: the tee error replaces it only when the underlying error is nil. In discard mode the tee receives the full input if present; otherwise the call uses `io.Discard.Write`. The base counter increases by the returned `n`. These branches explain why an interface comment about bytes sent cannot justify a universal client-delivery claim. [S3,T1,T2]

## ReadFrom: delegation and the revision

If a tee exists or discard is set, `httpFancyWriter.ReadFrom` uses `io.Copy(&f.basicWriter, r)` and returns immediately. The base `Write` path already updates its counter, so this branch does not add the returned count again. This preserves the written tee/discard routing rather than bypassing it through the original writer. Actual `io.Copy` behavior belongs to the runtime and reader/writer implementations; it was not executed here. [S5,T3,T4]

Otherwise the method asserts the original writer as `io.ReaderFrom`, calls `rf.ReadFrom(r)`, and records an implicit successful status only under `n > 0 && !f.basicWriter.wroteHeader`. It then adds `int(n)` to the byte counter and returns the same count and error. The selected code does not require `err == nil` for those accounting updates. It does not call the wrapper's `WriteHeader` in this direct branch. The factory's capability check explains the intended assertion path; arbitrary manual construction still needs a compatible underlying writer and is not guaranteed safe. [S1,S5]

The selected prior revision called `f.basicWriter.maybeWriteHeader()` before `rf.ReadFrom(r)`. The current direct branch updates recorded state after the delegate returns, conditional on a positive count and an unrecorded header. That is a documentation-relevant order/guard change, not proof of actual transport headers or general performance. The fallback's no-double-count structure is a separate current-source contract, not attributed to that selected historical change. [H1,S5]

## Example and written tests

A source-shaped usage fragment accepts an existing response writer; it starts no server:

```go
func observe(w http.ResponseWriter) int {
    wrapped := middleware.NewWrapResponseWriter(w, 1)
    wrapped.Discard()
    return wrapped.BytesWritten()
}
```

The fragment requires `net/http` and the module's `middleware` package in its surrounding file. It demonstrates wrapper construction and accessor use only; syntax review is not compilation or a runtime result. No setup or test command was run. [S1,S4]

The written tests cover flush status and suppression, ordinary tee writes, discard with and without a tee, byte counts in the tee `ReadFrom` path, and suppression of the original body in the discard `ReadFrom` path. The latter tests manually construct wrappers and assert the consumed count; they do not establish the factory's entire capability matrix. The helper `readerFromRecorder.ReadFrom` copies into the recorder body. These are documented assertions, not passed test results. [T1,T2,T3,T4,T5]

## FAQ

**Does every wrapper support `ReadFrom`?** No such universal contract appears in `WrapResponseWriter`; selection is capability-dependent. The selected HTTP2 comment is insufficient evidence. [S1,S2,S6]

**Are tee bytes counted twice?** The selected fallback returns the result of `io.Copy` without a second counter increment; base writes perform their own accounting. The written regression test expects one input-length count. [S3,S5,T3]

**Does discard mean the counter stays zero?** No. The base write path accounts for writes even when the original writer is bypassed, and written discard tests expect consumed bytes. [S3,T2,T4]

**Does direct `ReadFrom` always commit a wrapper header before reading?** No. The selected current method records state after the delegate call only under its positive-count/unrecorded-header guard. This is not a runtime guarantee about the original writer. [S5,H1]

## Maintenance across the selected local revisions

The new local target `c64ed7d6635f33a8b2feaff7dcfa55677023ac7d` has `9f8adb1aabaa8a91180a821111d3f8e668d1c0bf` as its direct parent. The complete tree comparison adds only `middleware/request_size_test.go`. The writer implementation, its selected tests, module declaration and license are byte-identical. The selected lexical caller contexts in `middleware/logger.go`, `middleware/middleware_test.go` and `middleware/wrap_writer_readfrom_test.go` are also unchanged. This is a bounded source comparison, not proof that every dynamic caller or runtime behavior is unchanged.

The new test declares four table cases for `RequestSize`: a smaller body, an exactly-at-limit body, a one-byte-over body and an empty body. In that written test, the handler calls `io.ReadAll` and writes `http.StatusRequestEntityTooLarge` on the error path. The `RequestSize` implementation already exists in the parent revision; its selected body assigns `http.MaxBytesReader` to `r.Body` and delegates to the handler, without an explicit `WriteHeader` call. Added assertions are not a newly introduced wrapper capability or passing test observations. Evidence: `middleware/request_size.go:9–17`; `middleware/request_size_test.go:14–61` at the new pin.

The original historical-pinned chapter needs no change to remain valid for its declared revision. This isolated version explicitly targets the new local pin, so its provenance is updated; it does not claim a wrapper behavior change. H1 remains the explicitly selected older `04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9`, not the immediate parent of the new target. No source project tests were executed.

## Evidence and limits

S1: source lines 15–44. S2: 46–81. S3: 83–128. S4: 130–148. S5: 211–229. S6: 203–209 and 231–248. T1: test lines 116–134. T2: 136–174. T3: 181–198. T4: 204–220. T5: 21–114. H1: same source path at `04f7f55a7b5ddb2ecd79a8d813b2256c1113b8a9`, `httpFancyWriter.ReadFrom`, frozen separately. Snapshots and native syntax selections are preserved beside this candidate. No private data, external changes, upstream execution, owner approval or training-gold promotion.
