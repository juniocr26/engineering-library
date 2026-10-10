# go-image-optimizer: implementation dossier

[English](go-image-optimizer.md) | [Português brasileiro](../../pt-BR/architecture/go-image-optimizer.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

## Image API and proxy contract

The Go router exposes `GET /health` and multipart POSTs `/images/compress`, `/images/resize/info`, `/images/resize`, `/images/convert/info`, `/images/convert` and `/images/preview`. The file field is `image`. Inspect routes return operation metadata; processing routes return image bytes with media type and download metadata. Compression keeps format family and oriented dimensions; resize changes dimensions within supported families; conversion changes family; preview supplies display bytes separately from download bytes. Unsupported variants are not equivalent to unsupported families.

Next.js routes under `/api/images` use a shared forwarding function. The browser sends same-origin multipart; the server reconstructs `FormData`, forwards to `BACKEND_URL`, propagates the request abort signal, reads the successful result into an `ArrayBuffer` and forwards format/dimension/disposition headers with `Cache-Control: no-store`. Backend non-success status/text is returned; forwarding exceptions become JSON 502. A missing backend Content-Type defaults to octet-stream. The browser never needs the Compose service hostname. No identity token is inserted, and this is not a public gateway with authorization or admission control.

The Go compression handler limits the whole request body to 50 MiB and uses 8 MiB as the multipart memory threshold before spill files. The proxy checks `File.size` after parsing multipart, so its 50 MiB file check is neither a streaming admission check nor exactly the Go total-body limit: multipart overhead can make a nominally allowed file exceed the backend limit. Processing uses actual bytes rather than trusting filename or client MIME. Shared processing errors map empty/corrupt input to 400, unsupported family to 415, resource excess to 413, unsupported variant to 422 and codec/unexpected failures to 500. Compression has its own mapping; do not infer all handlers are identical from one helper.

The response can grow. Byte reduction is an observation in the UI, not a contract. JSON info and binary results share the forwarding path, so consumers must respect Content-Type. Retrying repeats expensive processing; no job ID, history, idempotency key, durable result or asynchronous completion API exists.

## Resource and native-code boundaries

Encoded bytes are not decoded memory. The imaging layer bounds static dimensions at 32,000,000 pixels and animated canvas work at 64,000,000 frame-pixels. Dimension validation uses division to avoid multiplication overflow. An RGBA buffer at the static limit alone is about 128 million bytes; originals, destination buffers, frames, proxy buffers and codec allocations add more. Limits apply per operation, with variant-specific checks; they are not a global memory quota or concurrency limit. Some native decode work can precede later checks.

`UseCase.Execute` checks context before and after compression. It does not pass a cancellable context to the compressor. Forwarding an abort signal and setting HTTP timeouts therefore do not prove interruption of a synchronous native codec. The Go server sets 5 s header, 2 min read/write and 60 s idle timeouts. HTTP deadlines bound transport behavior; an encoder can continue consuming CPU before returning. A semaphore or separate worker process could provide admission and isolation, at complexity and communication cost; neither exists.

CGO and native codecs broaden HEIF/AVIF support and add ABI/build/security maintenance. Temporary multipart files are removed after successful parsing; file handles close; HEIF helpers clean up their temporary files. Request-scoped results do not constitute durable storage. Panic recovery in a handler does not sandbox a native library or recover from every native process failure. There is no implemented login, TLS termination or per-user rate limit in the reviewed app. Plan public exposure separately and never claim content validation alone makes hostile uploads safe.

## Deployment, diagnostics and evidence

Compose describes Go backend and Next.js frontend, plus test/development profiles. The backend runtime requires the native codec libraries supplied by its Dockerfile. Development bind mounts and dependency caches support editing; they are not a production rollout procedure. The frontend's server-side `BACKEND_URL` must resolve from its own runtime, typically `backend:8080` inside Compose. `localhost` there means that container, not the developer host or another service.

Diagnose separately: a proxy 502 suggests forwarding/abort/connectivity failure; a backend 4xx identifies invalid or unsupported input; a codec 500 suggests deployment or encoder failure; `/health` is liveness, not an all-format codec self-test. Inspect structured `slog` warnings/errors without logging image contents. Preserve a minimal non-sensitive reproducer and its actual format/variant. Backend HTTP tests, application fakes and imaging fixtures establish different boundaries; recorded historical builds/test results are not new validation. No browser, load, race or application execution occurred in this review.

There is no persistent upload database to back up and no migration process. Updating the backend must preserve matching runtime codec dependencies, and frontend/backend response metadata must remain compatible. Rolling back application images is conceptually possible with retained artifacts, but no release registry, production pipeline, TLS topology, rollback rehearsal or production SLO is evidenced. Benchmark categories are not applicable without measurements: pixel limits and byte-size UI output are not throughput benchmarks. Remaining gaps include concurrent memory peaks, interruption of native work, visual fidelity across representative variants and browser compatibility. Existing test documentation retains the historical native race/checkptr limitation.

## Supporting evidence

- [api/contracts](../../../../go-image-optimizer/docs/en/api/contracts.md)
- [security/resource-boundaries](../../../../go-image-optimizer/docs/en/security/resource-boundaries.md)
- [operations/deployment-and-diagnosis](../../../../go-image-optimizer/docs/en/operations/deployment-and-diagnosis.md)
- [Interview / Entrevista](../interviews/go-image-optimizer.md)
