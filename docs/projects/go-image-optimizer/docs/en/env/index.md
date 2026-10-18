# ENV — go-image-optimizer

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

## Docker Compose inputs

Each row describes behavior **at Compose interpolation**, before the application. `:-` uses the default for both missing and empty values; `:?` rejects both. An empty default is intentionally permitted at this layer. Final consumer behavior is described below.

[Source configuration](../../../../../../../go-image-optimizer/docker-compose.yml)

| Variable | Responsibility / consumer | Required | Missing | Empty | Safe example / default | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `BACKEND_PORT` | Network port / Compose and corresponding service | no | default | default | `8080` | L9 |
| `BACKEND_URL` | backend url | no | default | default | `http://backend:8080` | L32 |
| `FRONTEND_PORT` | Network port / Compose and corresponding service | no | default | default | `3000` | L36 |

## Application behavior

`PORT` is optional in Go: missing or empty uses `8080`; nonnumeric values or values outside 1–65535 fail. Compose fixes backend `8080` and Next `3000`. Direct `BACKEND_URL` uses `??`: missing uses `http://localhost:8080`, empty is retained and may form an invalid URL; Compose substitutes `http://backend:8080` for both. Never embed credentials in this URL. `HOSTNAME=0.0.0.0` exposes the container listener. `NODE_ENV=development` and `NEXT_TELEMETRY_DISABLED=1` are fixed in the dev profile. `CGO_ENABLED=1` enables codecs in backend-test. Optional test input `REAL_IMAGE_FIXTURES_DIR` falls back to test fixture paths when missing/empty; optional `TESTDATA_DIR` in preview_test.go similarly searches locally. These are not secrets or production inputs.

[Go config](../../../../../../../go-image-optimizer/backend/internal/config/config.go) · [Next proxy](../../../../../../../go-image-optimizer/frontend/app/api/images/forward-image-request.ts)
