# Go Image Optimizer technical interview study guide

[English](go-image-optimizer.md) | [Português brasileiro](../pt-BR/go-image-optimizer.md)

Study the problem, flows and decisions against the implementation. The functional scope is complete: compression, resizing, format conversion and preview fallback. Completion does not establish universal compatibility, measured production capacity or absence of limitations.

My main professional backend experience is PHP/Laravel; this portfolio is deliberate practical Go learning. Adapt suggested first-person answers to actual understanding. Do not memorize a script or invent production users/results. The source notes refer to checks on 2026-10-04; those are historical. Paths below refer to the `go-image-optimizer` repository. The URL Shortener guide supplied a question/answer structure, not facts or technologies for this project. Current development uses the existing Compose override and host dependency binds rather than named node_modules/.next volumes.

## Purpose and choices

### 1 What problem does it solve

I offer a simple upload, compress/resize/convert and download flow, with measured dimensions and byte sizes even when output grows. If the browser cannot display a backend-supported file, a generated preview provides display compatibility without changing download bytes.

The frontend keeps the selected original and temporary results. Compression retains family and oriented dimensions; Resize changes dimensions within the family; Convert changes family while retaining oriented dimensions. Preview is internal display support. Resize handles smaller images without cropping, advanced composition or an editor. The focused scope is complete; maintenance remains possible but additional features are not planned.

References: `README.pt-BR.md`, `frontend/app/components/image-upload/image-upload-form.tsx`.

### 2 Why Go with a PHP and Laravel background

The project lets me transfer transport/application/infrastructure reasoning while learning Go packages, small interfaces, explicit constructors, returned errors and resource lifetimes. It uses `net/http` without an HTTP framework or dependency-injection container. `NewRouter` constructs use cases and concrete dependencies; no Eloquent equivalent is needed because entities are not persisted.

Go is not automatically faster here. Decode, scaling, encode, upload and native libraries all contribute cost. The project demonstrates behavior, not benchmarked superiority over PHP.

References: `backend/internal/infrastructure/http/router.go`, `backend/internal/application/imagecompression/usecase.go`.

### 3 Why Next.js and React

React organizes selection, settings and result state; Next.js same-origin API routes forward multipart to Go. `app/page.tsx` composes Home, `ImageUploadForm` controls the flow, Resize/Convert modals configure it, `ImageSettingsDialog` shares modal behavior and `ImageResultModal` presents output. Tailwind supplies styling. `forward-image-request.ts` forwards cancellation and relevant status/headers.

Serving simpler HTML could meet the need. This separation adds a Node runtime and HTTP hop. The proxy reads FormData and buffers responses with arrayBuffer; it is not end-to-end streaming.

References: `frontend/app/api/images/forward-image-request.ts`, `frontend/app/components/image-upload/`.

### 4 Architecture terminology

This is a small layered architecture: HTTP handlers, operation coordination and pixel/codec infrastructure. It does not need a formal Clean Architecture claim or a microservices label merely because Node and Go use separate containers.

Compressor, Decoder/Source and Processor interfaces support useful test boundaries. Shared types live in `application/imageprocessing`; there are no persisted domain entities, repositories, database or DI framework. Another service would require independent operation/isolation/scale needs and measurements, not a diagram preference.

References: `docs/pt-BR/architecture.md`, `backend/internal/application/`, `backend/internal/infrastructure/`.

## End-to-end flows

### 5 Compression

The original goes through `/api/images/compress` to `POST /images/compress`. The handler validates multipart/body size, reads bytes and calls the use case. Compression detects the real byte family, checks limits, decodes and reencodes using that family. Bytes and download headers return; the UI measures the actual Blob.

The use case rejects empty input and checks context before/after `Compressor.Compress`, but that interface does not receive context and cannot interrupt internal compression. JPEG applies EXIF orientation; PNG best compression preserves pixels; other codecs have their own policies. Output can be larger. Persisting uploads would add retention/identity/recovery responsibilities not required by direct download.

References: `backend/internal/infrastructure/http/handler/compress_image/handler.go`, `backend/internal/infrastructure/imaging/compress/compressor.go`.

### 6 Resize inspection and settings

Opening the modal posts the original to `/api/images/resize/info`, returning oriented dimensions, family, MIME and frame count. Pixels mode preserves ratio or accepts independent dimensions; percentage mode offers 25%, 50% or 75% smaller. The frontend predicts dimensions; the backend recalculates from actual bytes.

Inspection decodes content rather than trusting names. Closing aborts inspection. Pixel defaults are original dimensions with ratio locked; the last edited dimension sets `axis`. Calculation tests cover rounding/limits, not real browser focus. Inspection followed by processing uploads/decodes again, accepting extra work to avoid server-side IDs and upload caches.

References: `frontend/app/components/image-resize/image-resize-modal.tsx`, `resize-options.ts`, `backend/internal/application/imageresize/usecase.go`.

### 7 Resize execution and download

Original bytes/options go to `/api/images/resize` and `/images/resize`. The use case validates options/calculates dimensions; decoded source pixels use Catmull–Rom and source-family encoding. Output includes original/result dimensions and a `_resized` name. The result modal replaces settings while the original remains selected.

Equal effective oriented dimensions return original bytes unchanged: no reencode or metadata removal. Actual resizing can change pixels, quality, palette and metadata. Normal repeated operations use the original, avoiding accumulated reencode loss; a user can still upload a previous result as a new original.

References: `backend/internal/application/imageresize/usecase.go`, `backend/internal/infrastructure/imaging/resize/decoder.go`, `frontend/app/components/image-upload/image-result-modal.tsx`.

### 8 Format conversion

Inspect the original, choose another family and send `image` plus `targetFormat`. Canonical destinations are jpeg, png, webp, avif, heif, gif, bmp and tiff. Static supported images retain oriented dimensions; returned MIME/extension match the output and larger results remain downloadable.

JPEG/JPG share a family but API requires jpeg, not jpg. HEIC/HEIF use heif as canonical target with HEVC, typically returning image/heic and .heic. Same-family, invalid targets and animations are rejected. Shared decoder restrictions reject APNG, AVIF sequences, multipage TIFF and unsupported multi-image HEIF. Besides UI inspection and processing, Execute calls Inspect and Processor.Convert decodes again; this is not a claim that all repeated decoding was optimized away.

References: `backend/internal/application/imageconversion/usecase.go`, `backend/internal/infrastructure/imaging/convert/processor.go`.

### 9 Preview fallback

Try native loading first, with display-only MIME correction for recognized signatures. On failure, send the real File/result Blob to `/api/images/preview`. The server returns a proportional thumbnail within 1200 × 1200 without enlargement: PNG for transparent pixels, JPEG for opaque pixels. Preview failure does not block operation/download.

The conversion decoder supplies restrictions and rejects animation; native browsers can display variants the fallback rejects. A session WeakMap caches bytes by Blob identity and shares concurrent consumers. It is not Redis, persistence or history. The actual file retains its own name, format, size and dimensions. No separate thumbnail configuration/cropping operation is offered.

References: `frontend/app/components/image-upload/browser-image-preview.tsx`, `preview-cache.ts`, `backend/internal/infrastructure/imaging/convert/preview.go`.

## Bytes pixels and codecs

### 10 Extension MIME and real format

Names and browser MIME are hints; signatures/container brands determine family, followed by variant validation and decode. JPEG named foto.png still follows JPEG processing; a correct extension does not make invalid bytes valid.

`DetectFormat` recognizes JPEG/PNG/GIF/BMP/TIFF, RIFF/WEBP and BMFF brands for AVIF/HEIF. RAW signatures including DNG/CR2 are rejected before TIFF routing. Detection alone does not prove valid content, supported variants or available codecs. Output MIME comes from encoded bytes. Download naming removes directory components, handles Windows separators and uses `mime.FormatMediaType`.

References: `backend/internal/infrastructure/imaging/detection.go`, `backend/internal/infrastructure/http/handler/imagehttp/filename.go`.

### 11 Decode transform and encode

Decode creates pixels; transformation applies orientation/scaling/transparency policy; encoding chooses representation. Family, pixels and file bytes are separate measures. `image.Image` describes coordinates/pixels, RGBA supports scaling and bytes.Buffer accumulates outputs where possible. HEIF's WriteToFile API requires a temporary file. The result contains bytes/family/MIME/dimensions/frame properties, not a persisted path.

A lossless encoder preserves the newly generated pixels, not the original image through resizing: interpolation already changed them.

References: `backend/internal/infrastructure/imaging/resize/decoder.go`, `convert/processor.go`, `imaging/heif.go`.

### 12 Fewer pixels do not guarantee fewer bytes

512 × 512 has 262,144 pixels; representation depends on codec, quality, alpha, palette and content. Halving both dimensions quarters pixel area, not necessarily file bytes. JPEG-to-BMP can grow substantially and remain valid.

File.size/Blob.size drive reduction/increase/no-change display; Content-Length matches returned bytes. Deterministic HTTP coverage checks a larger but downloadable BMP. A never-larger requirement would need another contract: retain original, reject, or choose parameters/formats rather than always delivering the requested family.

References: `frontend/app/components/image-convert/size-change.ts`, `frontend/tests/conversion-size.test.mjs`, `backend/internal/infrastructure/http/conversion_test.go`.

### 13 Encoding defaults

JPEG/WebP quality 82; AVIF/HEVC quality 60. Static WebP method 4/alpha quality 100; AVIF alpha 100/speed 6. PNG BestCompression; TIFF Deflate with predictor. GIF palette/BMP behavior differs from modern lossy codecs.

Quality scales are not interchangeable. JPEG/AVIF/HEVC defaults are lossy; PNG/TIFF preserve encoded input pixels. Compression/Resize retain detected static WebP lossless mode, whereas conversion uses lossy defaults. GIF conversion/Resize uses WebSafe quantization and Floyd–Steinberg dithering. These are code defaults, not documented outcomes of perceptual benchmarks; other requirements need measured visual quality, bytes and encoding costs.

References: `backend/internal/infrastructure/imaging/compress/compressor.go`, `resize/decoder.go`, `convert/processor.go`.

### 14 Aspect ratio rounding and enlargement

Locked ratio scales from width or height anchor; dimensions round to nearest integer with minimum one. Percentage reductions apply linearly to each dimension. Unlocked pixels accept independent width/height without cropping or padding.

Target uses `math.Round`, validates before float-to-int conversion and checks pixels by `MaxPixels/height` to avoid unsafe multiplication. 899 × 1599 at 50% smaller becomes 450 × 800; odd dimensions can slightly alter ratio. Enlargement interpolates rather than recovers lost detail. Square sample outputs 256 × 128 and 515 × 519 exercise independent axes.

References: `backend/internal/application/imageresize/usecase.go`, `frontend/app/components/image-resize/resize-options.ts`.

### 15 Resampling

`draw.CatmullRom.Scale` from golang.org/x/image/draw uses premultiplied RGBA and draw.Src in Resize/preview. It supplies smooth interpolation with more processing and possible edge ringing. Premultiplied alpha helps avoid dark halos around transparent edges. Scaling has no context parameter; cancellation is checked afterwards.

Nearest-neighbor suits pixel art but can alias photos; bilinear can smooth more simply. No project experiment establishes a universal quality winner. A different choice needs visual/cost evaluation.

References: `backend/internal/infrastructure/imaging/resize/decoder.go` (`scaleImage`), `backend/internal/infrastructure/imaging/convert/preview.go`.

### 16 Transparency

Conversion composites JPEG/BMP/HEIF onto white; PNG/WebP/AVIF/TIFF paths retain alpha. GIF uses binary transparency at a 50% threshold and can lose partial alpha/colors. The white canvas uses draw.Over. GIF dithering includes index correction so transparent pixels remain transparent while dark opaque pixels do not accidentally use the transparent entry.

Resize PNG/WebP tests include partial alpha; Resize BMP/HEIF use their encoder paths without conversion's explicit white compositing. Preview PNG preserves display alpha in its new pixels, not the original document/metadata. Keep original/result/preview separate.

References: `backend/internal/infrastructure/imaging/convert/processor.go`, `resize/animation.go`, `resize/resize_test.go`.

### 17 Orientation metadata and color

JPEG applies EXIF to pixels; AVIF autorotates; HEIF uses codec transformations. Conversion/preview attempt recognized EXIF in other static families. Do not promise universal EXIF/XMP/ICC copying or color fidelity.

Resize JPEG computes targets after orientation; synthetic orientation-6 tests check dimensions/red-blue placement and no obsolete orientation. Animated WebP Resize copies ICC, not EXIF/XMP; animated compression copies supported chunks. No-op Resize retains original bytes. Applying orientation is different from preserving the original field or every metadata record.

References: `backend/internal/infrastructure/imaging/orientation.go`, `resize/decoder.go`, `convert/processor.go`, `compress/webp.go`.

### 18 Animation and variants

Resize supports GIF/WebP reconstruction, timing and loops. AVIF sequences/animation are rejected because installed decoding cannot preserve finite-loop information. Conversion/fallback reject animations rather than silently flattening frames; APNG, multipage TIFF and unsupported multi-image HEIF are also rejected there.

GIF partial frames/disposal are composed then encoded as full frames, which can change palette/internal disposal representation. WebP decoder/encoder retains durations, loops and background. GIF compression uses gif.EncodeAll; AVIF compression uses DecodeAll/EncodeAll but real coverage is static, not proof of universal animation preservation. Family support does not imply all variants.

References: `backend/internal/infrastructure/imaging/resize/animation.go`, `variants.go`, `compress/avif.go`, `convert/processor.go`.

### 19 Libraries

Standard image/jpeg, image/png and image/gif; golang.org/x/image for BMP/TIFF/scaling; deepteams/webp; gen2brain/avif; strukturag/libheif bindings; GoMetadata for EXIF. go.mod declares Go 1.27 and direct libraries. WebP/AVIF have their own execution strategies, so not all codecs are exclusively Go code. Docker explicitly installs libheif/HEVC dependencies.

A detected valid family can fail when a decoder/encoder is unavailable. `ErrCodecUnavailable`, `ErrUnsupportedFormat` and `ErrInvalidImage` are distinct. Tested platform behavior does not establish every platform.

References: `backend/go.mod`, `backend/internal/infrastructure/imaging/heif.go`, `backend/internal/infrastructure/http/handler/imagehttp/errors.go`.

## Contracts resources and Go

### 20 HTTP contracts

GET /health and POST /images/compress, /images/resize/info, /images/resize, /images/convert/info, /images/convert, /images/preview. Browser image paths use /api prefix. Multipart supplies one `image`; Resize accepts options, conversion one canonical `targetFormat`.

Inspection returns width/height/format/contentType/frameCount JSON. Processing returns bytes, Content-Type/Length/Disposition and `_compressed`, `_resized` or `_converted` naming. Resize returns original/output dimensions; conversion adds X-Source-Format/X-Output-Format. Resize/conversion/preview use no-store; do not attribute every header to every route. Conversion rejects unknown/duplicate fields; info/preview accept image only. Resize rejects duplicate options and validates known options without the same general unknown-field rejection.

References: `backend/internal/infrastructure/http/router.go`, `handler/resize_image/handler.go`, `handler/convert_image/handler.go`.

### 21 Errors and filenames

JSON `error`: 400 invalid input/options, 413 limits, 415 unsupported family, 422 rejected variant, 500 internal/codec failure; proxy returns 502 if backend cannot be reached. Safe basename, operation suffix and byte-compatible extension determine download names.

Sentinel errors, errors.Is and fmt.Errorf with %w preserve categories. Handlers clean multipart temporaries and recover processing panics with slog diagnostics. Recovery does not resolve process/OOM failure. Filename sanitization is separate from content validation; foto.jpg can legitimately become foto_converted.png.

References: `backend/internal/infrastructure/http/handler/imagehttp/`, `handler/compress_image/filename.go`.

### 22 Resource limits

50 MiB body; 32 million decoded pixels; 64 million cumulative animation canvas pixels. Resize validates output dimensions/animation budget. Conversion checks encoded output ≤50 MiB after encoding, not before encoder memory allocation.

ParseMultipartForm's 8 MiB threshold is in-memory parsing before temporary files, not max upload. A 32-million-pixel RGBA buffer alone is about 128 million bytes before source/destination/frames/codec memory. GIF descriptors/WebP metadata get pre-decode checks where implemented; some AVIF compression frame checks happen after decode. No global admission control or concurrency benchmark exists, so simultaneous requests can multiply CPU/memory.

References: `backend/internal/infrastructure/imaging/limits.go`, `backend/internal/application/imageresize/usecase.go`, `convert/processor.go`.

### 23 Cancellation and timeouts

Cancellation is cooperative: frontend aborts obsolete requests, proxy forwards signal, Go checks ctx.Err and Resize checks between frames. Native codec/scaling calls cannot be forcibly stopped; Compressor lacks a context argument and the use case checks before/after.

ReadHeaderTimeout is 5 seconds, ReadTimeout/WriteTimeout 2 minutes and IdleTimeout 60 seconds. These are connection I/O bounds, not a hard encoder kill budget. Signals call Shutdown with a 10-second context, which also does not establish instant native-work termination. Strong isolation requirements would need measured budgets and perhaps process/admission mechanisms, not an assumed implemented feature.

References: `backend/internal/infrastructure/http/server.go`, `backend/cmd/api/main.go`, `application/imagecompression/usecase.go`.

### 24 Cleanup

`defer` closes multipart files and removes parser temporaries. HEIF creates an OS temporary, closes its descriptor, encodes, reads bytes and removes it on exit including error paths. Frontend URL creators revoke them when unused. MultipartForm.RemoveAll and os.Remove prevent durable upload storage; real test outputs stay in memory.

Native libraries own additional lifecycles; explicit file cleanup does not prove zero native leaks. Go's collector does not universally remove files or external resources. Like PHP/Laravel, resource ownership matters; defer keeps cleanup near acquisition.

References: `backend/internal/infrastructure/imaging/heif.go`, `handler/convert_image/handler.go`, `handler/resize_image/handler.go`.

### 25 File Blob and Object URL

File is a Blob with name/type information. Blob contains original/result/preview bytes; an Object URL is a temporary browser reference, not a public server address. Each identity has a distinct purpose.

ImageUploadForm owns selected/result state; BrowserImagePreview creates/revokes display URLs. PreviewSession ignores stale responses; acquirePreview shares a promise by Blob identity, counts consumers and aborts incomplete generation when the last consumer leaves. Cache holds bytes, not permanent URLs; reload clears it. No localStorage/IndexedDB. Downloading preview bytes would violate actual result format/name/size/dimensions.

References: `frontend/app/components/image-upload/preview-cache.ts`, `browser-image-preview.tsx`, `image-upload-form.tsx`.

### 26 Interfaces errors and dependency construction

Small interfaces follow use-case needs: Compressor processes bytes; Decoder yields a request-scoped Source; Processor inspects/converts. NewRouter supplies concrete dependencies to NewUseCase constructors. Go interface satisfaction is implicit method matching, without implements. Errors are returned and classified with errors.Is.

Shared compression aliases maintain compatibility. Conversion also asserts access to Pixels on the shared concrete decoder, so acknowledge limited decoupling. This resembles Laravel services/contracts but does not use its container; useful test doubles do not make all packages completely independent of infrastructure.

References: `backend/internal/application/imageprocessing/image.go`, `imagecompression/usecase.go`, `imageresize/usecase.go`, `imageconversion/usecase.go`, `imaging/convert/processor.go`.

## Docker tests and evidence

### 27 CGO and Docker dependencies

HEIF bindings call native libheif, requiring CGO. Go 1.27.1 Alpine development/build uses build-base, pkgconf, libheif-dev, libheif-libde265 and libheif-x265. Alpine 3.24 runtime includes libheif/plugins and a non-root user; no Go compiler in the final runtime.

Headers come from libheif-dev; libde265 decodes HEVC, x265 encodes. CGO_ENABLED=1 does not make the binary static/self-contained. Tests keep the toolchain/headers/plugins. ADR 001 explains why the old static distroless runtime no longer fits. Separate Node/native environments help builds but do not prove HA or independent physical failure domains.

References: `backend/Dockerfile`, `frontend/Dockerfile`, `docs/pt-BR/adr/001-native-image-codecs.md`.

### 28 Reproducing development and checks

Install according to `docs/en/docker-development-setup.md`, then from the subject repository use:

```sh
docker compose -f docker-compose.yml -f compose.development.yaml --profile dev up -d backend frontend-dev
docker compose -f docker-compose.yml -f compose.development.yaml --profile test run --rm --no-deps -T backend-test go test -count=1 ./...
docker compose -f docker-compose.yml -f compose.development.yaml --profile dev exec -T frontend-dev node --test tests/resize-options.test.mjs tests/conversion-size.test.mjs tests/preview-cache.test.mjs
docker compose -f docker-compose.yml -f compose.development.yaml --profile dev exec -T frontend-dev npx tsc --noEmit
# Build with the production environment override; this is a build, not a browser check.
docker compose -f docker-compose.yml -f compose.development.yaml --profile dev run --rm --no-deps -e NODE_ENV=production frontend-dev npm run build
docker compose -f docker-compose.yml -f compose.development.yaml --profile dev stop frontend-dev backend
```

Backend fixtures mount read-only; runtime backend has no compiler. Host binds store frontend dependencies/artifacts, not uploads/history. npm ci uses the lockfile. Rebuild appropriate images for Dockerfile/toolchain/native changes. Historical 2026-10-04 checks included baseline/expanded/full Go tests, 12 frontend tests, TypeScript and production build; browser, load and new race checks were not performed. New results are in the subject project's `docs/en/verification.md`.

References: `docker-compose.yml`, `compose.development.yaml`, `docs/en/testing.md`, `docs/en/docker.md`.

### 29 Real-sample tests

Nine physical static 512 × 512 samples remain inputs. Resize runs 36 transformations: each sample at proportional 256 × 256 and 516 × 516, independent 256 × 128 and 515 × 519, plus nine unchanged-byte cases. Independent codec decoding checks actual output dimensions instead of trusting headers.

Conversion runs nine sources × eight destinations: 63 valid conversions and nine same-family rejections. Tests check family, MIME, oriented dimensions, one frame, source bytes and alpha/compositing where applicable. Fixture inventory changes require explicit policy. Synthetic tests cover EXIF, partial alpha, GIF disposal/timing/loops, animated WebP, AVIF animation/APNG/multipage TIFF rejection and budgets. Small HTTP tests cover all destination names/extensions/MIME/no-store/dimensions/body length without repeating the expensive matrix.

References: `backend/internal/infrastructure/imaging/resize/resize_test.go`, `convert/real_fixtures_test.go`, `backend/internal/infrastructure/http/conversion_test.go`.

### 30 What passing tests do not prove

Covered cases passed in the stated environment, not universal compatibility, perceptual perfection, concurrent safety or production capacity. Static square fixtures need complementary orientation/animation synthetics. Function/cache tests do not exercise real browser layout/focus/download or cross-browser behavior; TypeScript/build check compilation.

A historical race/checkptr failure in libheif remains documented and was not rerun. No benchmark or coverage percentage is claimed. To extend evidence, define a requirement and representative cases/metrics, separating functional, visual, browser, concurrency and performance observations.

References: `docs/en/testing.md`, `frontend/tests/`, `docs/en/docker.md`.

## Scope decisions

### 31 Why no history database Redis queue or worker

Results return directly and session state stays in the browser. No retrieval by ID, history queries or post-response jobs are required. SQLite/other databases, Redis, brokers, workers and object storage would add retention/recovery/retries/operations outside scope.

Synchronous processing occupies requests and costs CPU/memory; transient state means reload loss and reupload. Resize covers smaller-image needs, without a separate thumbnail operation or Paint-like composition. New future job/recovery requirements could change design, but none is planned and no production-readiness claim follows.

References: `README.pt-BR.md`, `docs/pt-BR/architecture.md` trade-offs.

### 32 Lessons and honest experience

Distinguish bytes/names, pixels/file size, destination alpha/animation support, orientation/metadata preservation and cooperative cancellation/native interruption. Learning Go requires understanding these contracts, verifying real bytes and managing native dependencies, not merely syntax.

Variant/color/metadata/resource/cancellation limits remain; absent global concurrency control/measurement limits scale claims. Do not assign undocumented development steps to humans or AI. Describe only assistance actually used and demonstrable; walk from handler through application rule, codec and test, including limited abstractions.

References: `docs/pt-BR/architecture.md`, `backend/internal/infrastructure/imaging/`, `docs/pt-BR/testing.md`.

## Interview summaries

About sixty seconds: My professional background is PHP/Laravel and this is practical Go learning. A Next.js UI compresses, resizes and converts images, with preview fallback. Multipart goes through Next.js to Go, which detects byte families, validates variants/limits, decodes/transforms/encodes and returns measured downloadable bytes without persistence. HEIF uses CGO/libheif. Tests cover nine samples, four Resize transforms and eight conversion destinations plus orientation, alpha, animation and HTTP. Scope is complete; scale, universal metadata preservation and production readiness are not claimed.

About thirty seconds: A Go/Next.js image-processing portfolio supporting compression, resize, conversion and fallback. Byte detection/resource limits precede direct results without database/history. Real-file tests verify dimensions, orientation and alpha, with explicit variant/metadata/resource/cancellation limits.

## Decision matrix

| Decision | Benefit | Cost |
| --- | --- | --- |
| Synchronous/transient processing | Direct result/simple lifecycle | Occupied request, reload loss, no ID recovery |
| Separate inspection | Server-validated settings | Reupload/redecode |
| Shared decoder | Common Resize/convert/preview policy | Coupling and compression differences |
| CGO/libheif | Real HEIF processing | C libraries/plugins |
| Native preview with fallback | Display compatibility | Extra upload, animation rejection |
| Catmull–Rom | Smooth interpolation | CPU and possible ringing |
| Fixed encoding defaults | Predictable behavior | Loss/size not universally guaranteed |
| White composition/binary GIF | Explicit destination policy | Alpha/color loss |
| Variant rejection | No silent flattening | Limited compatibility |
| Real-output tests | Byte/contract evidence | No measured perceptual quality/scale |
| Finished scope | Focused demonstrable project | No editor, separate thumbnails or job infrastructure |

## Claims to avoid

Do not claim professional Go experience instead of portfolio learning; universal size reduction; conversion improving quality; arbitrary variants; metadata-preserving display previews; lossless resizing merely because an encoder is lossless; instant codec cancellation; microservices from two containers; scale from tests; universal animation support; a planned history/queue roadmap; or production readiness. State the corresponding tested behavior and limitation.

## Reasoning practice

Problem → requirement → alternatives → decision → benefit → cost → failure → current handling → limitation. Separate implemented facts, consequences and future hypotheses; no measurement means no technology-based performance promise.

For preview, compare a message-only UI, client decoders and server thumbnails. Current native-first/fallback policy displays supported static content without changing downloads, at extra decode/cache/URL cost. Codec failure, rejected variants and stale requests get local error/retry, consumer cancellation and stale-result rejection; animation/metadata/browser universality remain unproven.

For Resize, explain linear percentages versus bytes, then trace math.Round, pixel ceiling, Catmull–Rom, family encoding and independent test decoding. Larger output remains valid and honestly presented. Locate cooperative checks and non-interruptible calls.

Review scope in the subject README, contracts/trade-offs in architecture, environment in Docker/development setup, checks versus results in testing/verification and physical sample inventory in testing. Read the referenced implementations before defending a decision.

## Source-review follow-ups and ordered study — 2026-10-09

The [Resize contract](../../../go-image-optimizer/docs/en/architecture.md) distinguishes defaults precisely: omitted or empty `axis` uses `width`; an explicitly empty `keepAspectRatio` is rejected. Required numeric fields still reject empty values. Do not infer one universal empty-field policy from the shared modal or handler helpers.

**Question: Is the 50 MiB client file check identical to the server limit?** Model answer: “The proxy checks image.size after parsing FormData, while Go caps the entire multipart request body. Multipart overhead counts on the backend, so a file near the boundary can pass the file check and fail the request limit. Neither check establishes a total process-memory cap.”

**Deeper questions:** Why do socket timeouts not stop codecs? Can a no-op Resize preserve metadata even when real resizing does not? Why do identical bytes in two Blobs create distinct preview cache entries? What do calculation/cache tests fail to establish about browser focus and downloads?

Study order: original/result/display bytes and HTTP contracts → byte detection/variant policies → use-case interfaces and errors → dimension math/orientation/alpha/animation → native codecs and cancellation/resource boundaries → frontend state/preview lifetimes → tests and historical evidence → conditional alternatives. No extra product features are planned, and this study sequence marks no completed topics. This audit used source inspection only; historical tests/builds above were not repeated.
