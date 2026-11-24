# Compression use case: error results, context checks and delegation

Source-reviewed experimental chapter authored by Codex, pending human approval. Frozen revision: go-image-optimizer `48476de6e4450294b7769ab7af90805100bb21b5`. Relevant files are `backend/internal/application/imagecompression/usecase.go` and `backend/internal/infrastructure/imaging/compress/compressor.go`. The actual agent arms `gio-compression-flow-caller` and `gio-compression-flow-helpers` were preserved; both were refused for insufficient declaration-specific explanation. No external application code was executed.

## Construction stores an injected dependency

The application declares a `Compressor` interface with one method taking image bytes and returning a result plus an error. Its `UseCase` struct stores a value of that interface in an unexported field. The constructor `NewUseCase` returns a value containing the supplied dependency. It does not choose a concrete encoder, call compression or inspect an input image during construction.

This boundary limits what a source-only explanation can connect. Another package defines a concrete type with a compatible method, but two matching method names do not establish the actual object injected at runtime. The original supplied files showed a possible structural relationship without the composition root. The additional router source below now establishes one explicit construction path; an actually running injected object is still not observed. A different implementation, test double or invalid dependency can be supplied through other code. This chapter therefore documents the application method and the concrete method separately.

## Execute checks input before consulting the context

The declaration `UseCase.Execute(ctx context.Context, input []byte) (Result, error)` receives a context and the image bytes. Its first guard is `len(input) == 0`. This branch returns `Result{}, ErrEmptyImage` immediately. It runs before either context check and before invoking the stored compressor. Reordering these guards in prose can change which error appears when multiple preconditions fail.

For a nonempty input, the method calls `ctx.Err()` and returns a zero result with that error when non-nil. There is no explicit nil-context guard in this body. Passing the first check leads to `u.compressor.Compress(input)`. The context is not an argument of that interface call. The body does not establish that compression can be interrupted halfway through, nor does it launch a background task or impose a separate timer around the operation.

## Three later outcomes preserve result and error roles

If the compression call returns a non-nil error, the method returns `Result{}, err`. A result returned alongside that error is discarded by this application boundary. If compression reports success, the body checks the context again. A non-nil result from the second context check also replaces the computed result with a zero result and returns the context error. Only after both successful checks and a successful compression call does the method return `result, nil`.

The second check is therefore observable even though the context was not passed into the interface method. It can prevent returning the computed image after the context reports an error. It does not demonstrate that already performed compression work was undone. Both drafts omitted the exact zero-result handoff; only the helper arm omitted the second context check. The caller-only arm explicitly mentioned that second check. Error propagation here means returning the inspected error; no retry, exception handler, compensating action or successful-runtime guarantee is present in the method.

## The concrete compressor dispatches after detection

The separate method `Compressor.Compress` first invokes `imaging.DetectFormat(input)`. Its non-nil error path returns a zero result and that error before the switch. The switch then returns directly from a format-specific helper for each of eight named formats: JPEG, PNG, WebP, AVIF, HEIF, GIF, BMP and TIFF. The HEIF branch additionally passes `detected.ContentType`; the other listed branches pass the input alone.

The default switch branch returns a zero result with `imagecompression.ErrUnsupportedFormat`. These statements show dispatch and direct forwarding of helper results. They do not establish how every codec validates dimensions, handles animation, changes metadata or allocates memory, because those helper bodies are absent from this packet. Detection and encoding are different source responsibilities; neither is equivalent to the application's context policy.

## What the corrected chapter establishes

Both neural arms used generic compression prose and omitted the declaration names required by the writer. Adding the concrete dispatch method did not recover the application's context ordering or prove its runtime binding. This correction preserves the early empty-input result, both context checks, zero-result error paths and final success result, then describes concrete format dispatch within its own evidence. The original unsuccessful outputs remain diagnostic artifacts. This is an authored documentation candidate, not an approved training example, an execution trace of the application or evidence of changed model weights.

## Engineer FAQ and verified static composition

<!-- reading-section: faq:concrete-compressor-composition -->
### Which source connects the concrete compressor to the application interface?

The added router constructs `imagecompression.NewUseCase(compress.NewCompressor())` and supplies it to the compression handler factory for `POST /images/compress`. The returned handler later calls the supplied use case with the request context and uploaded image bytes. This verifies a written composition path, not an executed deployment or every possible constructor caller.

<!-- reading-section: faq:cancellation-boundary -->
### Does cancellation interrupt the concrete Compress call halfway through?

The interface call receives the input bytes without a context argument. The application checks the context before and after it. A later context error can discard the computed result, but this body does not demonstrate interruption or rollback of already performed codec work.

<!-- reading-section: faq:error-result-handoff -->
### Does a compressor result returned with an error reach the successful response?

The use case replaces that result with its zero Result on the error branch. The inspected HTTP handler separately delegates non-nil errors to its error helper and only writes the successful result data on its later success path. Exact error-helper mapping and actual network delivery remain outside this added evidence.

```mermaid
flowchart LR
  R["NewRouter"] --> C["compress.NewCompressor"]
  C --> U["imagecompression.NewUseCase"]
  U --> H["ProcessImage handler factory"]
  H --> E["UseCase.Execute with request context and bytes"]
  E --> K["Compressor.Compress with bytes"]
  K --> D["DetectFormat then codec helper"]
```

The diagram shows source construction and call direction. Request parsing, context guards and error branches remain conditional as described above; no server, upload or codec was executed for this review.
