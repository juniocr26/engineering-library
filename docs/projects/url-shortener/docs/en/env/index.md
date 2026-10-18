# ENV — url-shortener

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

## Docker Compose inputs

Each row describes behavior **at Compose interpolation**, before the application. `:-` uses the default for both missing and empty values; `:?` rejects both. An empty default is intentionally permitted at this layer. Final consumer behavior is described below.

[Source configuration](../../../../../../../url-shortener/compose.yaml)

| Variable | Responsibility / consumer | Required | Missing | Empty | Safe example / default | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `CASSANDRA_CLUSTER_NAME` | cassandra cluster name / Cassandra, FastAPI | no | default | default | `url_shortener_cluster` | L15 |
| `CASSANDRA_DATACENTER` | cassandra datacenter / Cassandra, FastAPI | no | default | default | `datacenter1` | L16 |
| `CASSANDRA_RACK` | cassandra rack / Cassandra, FastAPI | no | default | default | `rack1` | L17 |
| `CASSANDRA_ENDPOINT_SNITCH` | cassandra endpoint snitch / Cassandra, FastAPI | no | default | default | `GossipingPropertyFileSnitch` | L18 |
| `CASSANDRA_SEEDS` | cassandra seeds / Cassandra, FastAPI | no | default | default | `cassandra-1` | L19 |
| `CASSANDRA_USERNAME` | cassandra username / Cassandra, FastAPI | yes | Compose error | Compose error | `Set CASSANDRA_USERNAME in .env` | L20 |
| `CASSANDRA_PASSWORD` | cassandra password / Cassandra, FastAPI | yes | Compose error | Compose error | `<secret>` | L21 |
| `CASSANDRA_MAX_HEAP_SIZE` | cassandra max heap size / Cassandra, FastAPI | no | default | default | `512M` | L22 |
| `CASSANDRA_HEAP_NEWSIZE` | cassandra heap newsize / Cassandra, FastAPI | no | default | default | `128M` | L23 |
| `PYTHON_VERSION` | python version | no | default | default | `3.14` | L40 |
| `UV_VERSION` | uv version | no | default | default | `0.8.17` | L41 |
| `APP_UID` | File ownership / build or container user | no | default | default | `1000` | L42 |
| `APP_GID` | File ownership / build or container user | no | default | default | `1000` | L43 |
| `APP_PORT` | Network port / Compose and corresponding service | no | default | default | `8000` | L58 |
| `APP_ENV` | app env | no | default | default | `development` | L63 |
| `APP_HOST` | app host | no | default | default | `0.0.0.0` | L64 |
| `REDIS_HOST` | redis host / Redis, FastAPI | no | default | default | `redis` | L66 |
| `REDIS_PORT` | Network port / Compose and corresponding service | no | default | default | `6379` | L67 |
| `REDIS_DB` | redis db / Redis, FastAPI | no | default | default | `0` | L68 |
| `REDIS_PASSWORD` | redis password / Redis, FastAPI | no | default | default | `""` | L69 |
| `CASSANDRA_CONTACT_POINTS` | cassandra contact points / Cassandra, FastAPI | no | default | default | `cassandra-1,cassandra-2,cassandra-3` | L70 |
| `CASSANDRA_PORT` | Network port / Compose and corresponding service | no | default | default | `9042` | L71 |
| `CASSANDRA_KEYSPACE` | cassandra keyspace / Cassandra, FastAPI | no | default | default | `url_shortener` | L72 |
| `SHORT_URL_BASE` | short url base | no | default | default | `http://localhost:8000` | L76 |
| `URL_ID_START` | url id start | no | default | default | `14776336` | L77 |
| `BASE62_ALPHABET` | base62 alphabet | no | default | default | `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz` | L78 |
| `OBFUSCATING_KEY` | obfuscating key | no | default | default | `""` | L79 |
| `BASIC_AUTH_USERNAME` | basic auth username | no | default | default | `""` | L80 |
| `BASIC_AUTH_PASSWORD` | basic auth password | no | default | default | `""` | L81 |

## Direct Python configuration

Python inputs are optional with the defaults below; Compose requires nonempty Cassandra bootstrap credentials.

| Variable | Missing / default | Empty |
| --- | --- | --- |
| `APP_ENV` | `"development"` | retained, no fallback; validity depends on consumer |
| `APP_HOST` | `"0.0.0.0"` | retained, no fallback; validity depends on consumer |
| `APP_PORT` | `8000` | ValueError: startup fails |
| `BASIC_AUTH_USERNAME` | `None` | None: disables option; intentional |
| `BASIC_AUTH_PASSWORD` | `None` | None: disables option; intentional |
| `REDIS_HOST` | `"redis"` | retained, no fallback; validity depends on consumer |
| `REDIS_PORT` | `6379` | ValueError: startup fails |
| `REDIS_DB` | `0` | ValueError: startup fails |
| `REDIS_PASSWORD` | `None` | None: disables option; intentional |
| `CASSANDRA_CONTACT_POINTS` | `"cassandra-1,cassandra-2,cassandra-3"` | ValueError: requires at least one item |
| `CASSANDRA_PORT` | `9042` | ValueError: startup fails |
| `CASSANDRA_KEYSPACE` | `"url_shortener"` | retained, no fallback; validity depends on consumer |
| `CASSANDRA_USERNAME` | `None` | None: disables option; intentional |
| `CASSANDRA_PASSWORD` | `None` | None: disables option; intentional |
| `CASSANDRA_DATACENTER` | `"datacenter1"` | retained, no fallback; validity depends on consumer |
| `SHORT_URL_BASE` | `"http://localhost:8000"` | retained, no fallback; validity depends on consumer |
| `URL_ID_START` | `62**4` | ValueError: startup fails |
| `BASE62_ALPHABET` | `"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"` | retained, no fallback; validity depends on consumer |
| `OBFUSCATING_KEY` | `None` | None: disables option; intentional |

`BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` enable authentication only when both are nonempty. Cassandra authentication also needs the complete pair. Missing/empty `REDIS_PASSWORD` disables password authentication; Compose configures Redis correspondingly. Missing/empty `OBFUSCATING_KEY` disables obfuscation, which is not encryption. `SHORT_URL_BASE` must match the public URL; `BASE62_ALPHABET` and `URL_ID_START` must preserve existing ID compatibility. Never publish credentials or tokens. Heap, snitch, rack and seeds configure the Cassandra image: Compose defaults were verified; additional image-internal processing was not audited.

[Python settings](../../../../../../../url-shortener/app/core/config.py)
