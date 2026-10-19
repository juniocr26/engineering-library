# Image API and proxy contract

[English](contracts.md) | [Português brasileiro](../../pt-BR/api/contracts.md)

Static source review: 2026-10-10. Implemented facts, general theory and hypothetical changes are distinguished below. Runtime commands were not executed.

The Go router exposes `GET /health` and multipart POSTs `/images/compress`, `/images/resize/info`, `/images/resize`, `/images/convert/info`, `/images/convert` and `/images/preview`. The file field is `image`. Inspect routes return operation metadata; processing routes return image bytes with media type and download metadata. Compression keeps format family and oriented dimensions; resize changes dimensions within supported families; conversion changes family; preview supplies display bytes separately from download bytes. Unsupported variants are not equivalent to unsupported families.

Next.js routes under `/api/images` use a shared forwarding function. The browser sends same-origin multipart; the server reconstructs `FormData`, forwards to `BACKEND_URL`, propagates the request abort signal, reads the successful result into an `ArrayBuffer` and forwards format/dimension/disposition headers with `Cache-Control: no-store`. Backend non-success status/text is returned; forwarding exceptions become JSON 502. A missing backend Content-Type defaults to octet-stream. The browser never needs the Compose service hostname. No identity token is inserted, and this is not a public gateway with authorization or admission control.

The Go compression handler limits the whole request body to 50 MiB and uses 8 MiB as the multipart memory threshold before spill files. The proxy checks `File.size` after parsing multipart, so its 50 MiB file check is neither a streaming admission check nor exactly the Go total-body limit: multipart overhead can make a nominally allowed file exceed the backend limit. Processing uses actual bytes rather than trusting filename or client MIME. Shared processing errors map empty/corrupt input to 400, unsupported family to 415, resource excess to 413, unsupported variant to 422 and codec/unexpected failures to 500. Compression has its own mapping; do not infer all handlers are identical from one helper.

The response can grow. Byte reduction is an observation in the UI, not a contract. JSON info and binary results share the forwarding path, so consumers must respect Content-Type. Retrying repeats expensive processing; no job ID, history, idempotency key, durable result or asynchronous completion API exists.

## Multipart differences verified on 2026-10-19

The shared proxy does not make backend handlers equivalent. Compression calls `FormFile("image")` without the exact-one-file checks of resize/conversion. Resize rejects repeated text values; missing/empty `axis` becomes `width`, missing `keepAspectRatio` becomes true and explicit empty is invalid. Conversion requires exactly one `targetFormat`; its inspection and preview reject extra text fields. Resize inspection does not run the processing-options parser. Consumers should validate per operation instead of applying one universal multipart schema.

All reviewed handlers set a 50 MiB total-body bound in Go; 8 MiB is a multipart memory threshold, not a complete upload or process-memory cap. Next checks one selected file after parsing FormData. Encoded-body overhead and response buffering remain separate resource costs. See [current FAQ](../faq/index.md) and the [inspection record](../operations/documentation-audit-2026-10-19.md).
