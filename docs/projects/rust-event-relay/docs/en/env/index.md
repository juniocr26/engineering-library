# ENV — rust-event-relay

[Project index](../index.md)

Verified on 2026-10-18 from safe local source files. Actual `.env` values were not used in this reference. Secret examples use `<secret>`. Never publish passwords, tokens or credential-bearing URLs; preserve existing cluster credentials. Shell variables can override the Compose environment file.

## Docker Compose inputs

Each row describes behavior **at Compose interpolation**, before the application. `:-` uses the default for both missing and empty values; `:?` rejects both. An empty default is intentionally permitted at this layer. Final consumer behavior is described below.

[Source configuration](../../../../../../../rust-event-relay/compose.yaml)

| Variable | Responsibility / consumer | Required | Missing | Empty | Safe example / default | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `LOCAL_UID` | File ownership / build or container user | no | default | default | `1000` | L7 |
| `LOCAL_GID` | File ownership / build or container user | no | default | default | `1000` | L8 |
| `HOST_FRONTEND_PORT` | Network port / Compose and corresponding service | no | default | default | `5173` | L21 |
| `POSTGRES_HOST_PORT` | Network port / Compose and corresponding service | no | default | default | `5433` | L22 |
| `RABBITMQ_MANAGEMENT_PORT` | Network port / Compose and corresponding service | no | default | default | `15672` | L23 |
| `HTTP_METRICS_ADDR` | http metrics addr | no | default | default | `127.0.0.1:9100` | L24 |
| `RELAY_METRICS_ADDR` | relay metrics addr limit, timing or topology / Rust worker | no | default | default | `127.0.0.1:9101` | L25 |
| `CONSUMER_METRICS_ADDR` | consumer metrics addr limit, timing or topology / Rust worker | no | default | default | `127.0.0.1:9102` | L26 |
| `CONSUMER_NAME` | consumer name limit, timing or topology / Rust worker | no | default | default | `inventory.stock.v1` | L27 |
| `CONSUMER_PREFETCH` | consumer prefetch limit, timing or topology / Rust worker | no | default | default | `1` | L28 |
| `CONSUMER_SOURCE_EXCHANGE` | consumer source exchange limit, timing or topology / Rust worker | no | default | default | `relay.events` | L29 |
| `CONSUMER_SOURCE_QUEUE` | consumer source queue limit, timing or topology / Rust worker | no | default | default | `relay.local` | L30 |
| `CONSUMER_SOURCE_ROUTING_KEY` | consumer source routing key limit, timing or topology / Rust worker | no | default | default | `event` | L31 |
| `CONSUMER_QUARANTINE_EXCHANGE` | consumer quarantine exchange limit, timing or topology / Rust worker | no | default | default | `relay.quarantine` | L32 |
| `CONSUMER_QUARANTINE_QUEUE` | consumer quarantine queue limit, timing or topology / Rust worker | no | default | default | `relay.quarantine.inventory` | L33 |
| `CONSUMER_QUARANTINE_ROUTING_KEY` | consumer quarantine routing key limit, timing or topology / Rust worker | no | default | default | `inventory` | L34 |
| `CONSUMER_OPERATION_MS` | consumer operation ms limit, timing or topology / Rust worker | no | default | default | `10000` | L35 |
| `CONSUMER_RECONNECT_MS` | consumer reconnect ms limit, timing or topology / Rust worker | no | default | default | `5000` | L36 |
| `CONSUMER_DRAIN_MS` | consumer drain ms limit, timing or topology / Rust worker | no | default | default | `15000` | L37 |
| `CONSUMER_SHUTDOWN_MS` | consumer shutdown ms limit, timing or topology / Rust worker | no | default | default | `25000` | L38 |
| `CONSUMER_POOL_MAX` | consumer pool max limit, timing or topology / Rust worker | no | default | default | `2` | L39 |
| `CONSUMER_POOL_ACQUIRE_MS` | consumer pool acquire ms limit, timing or topology / Rust worker | no | default | default | `5000` | L40 |
| `CONSUMER_STATEMENT_MS` | consumer statement ms limit, timing or topology / Rust worker | no | default | default | `5000` | L41 |
| `CONSUMER_LOCK_MS` | consumer lock ms limit, timing or topology / Rust worker | no | default | default | `3000` | L42 |
| `REPLAY_OPERATORS` | replay operators | no | default | default | `""` | L43 |
| `RELAY_MAINTENANCE_CANDIDATES` | relay maintenance candidates limit, timing or topology / Rust worker | no | default | default | `""` | L44 |
| `RELAY_LEASE_MS` | relay lease ms limit, timing or topology / Rust worker | no | default | default | `60000` | L45 |
| `RELAY_IDLE_MS` | relay idle ms limit, timing or topology / Rust worker | no | default | default | `1000` | L46 |
| `RELAY_FAILURE_MS` | relay failure ms limit, timing or topology / Rust worker | no | default | default | `1000` | L47 |
| `RELAY_RECONNECT_MS` | relay reconnect ms limit, timing or topology / Rust worker | no | default | default | `5000` | L48 |
| `RELAY_POOL_MAX` | relay pool max limit, timing or topology / Rust worker | no | default | default | `2` | L49 |
| `RELAY_POOL_ACQUIRE_MS` | relay pool acquire ms limit, timing or topology / Rust worker | no | default | default | `5000` | L50 |
| `RELAY_STATEMENT_MS` | relay statement ms limit, timing or topology / Rust worker | no | default | default | `5000` | L51 |
| `RELAY_LOCK_MS` | relay lock ms limit, timing or topology / Rust worker | no | default | default | `3000` | L52 |
| `RELAY_DRAIN_MS` | relay drain ms limit, timing or topology / Rust worker | no | default | default | `15000` | L53 |
| `RELAY_SHUTDOWN_MS` | relay shutdown ms limit, timing or topology / Rust worker | no | default | default | `25000` | L54 |
| `RABBITMQ_CONNECT_TIMEOUT_MS` | rabbitmq connect timeout ms / broker, Rust AMQP | no | default | default | `10000` | L55 |
| `RABBITMQ_PUBLISH_TIMEOUT_MS` | rabbitmq publish timeout ms / broker, Rust AMQP | no | default | default | `10000` | L56 |
| `RABBITMQ_EXCHANGE` | rabbitmq exchange / broker, Rust AMQP | no | default | default | `relay.events` | L57 |
| `RABBITMQ_QUEUE` | rabbitmq queue / broker, Rust AMQP | no | default | default | `relay.local` | L58 |
| `RABBITMQ_ROUTING_KEY` | rabbitmq routing key / broker, Rust AMQP | no | default | default | `event` | L59 |
| `RABBITMQ_DEFAULT_USER` | rabbitmq default user / broker, Rust AMQP | yes | Compose error | Compose error | `Set RABBITMQ_DEFAULT_USER in .env` | L62 |
| `RABBITMQ_DEFAULT_PASS` | rabbitmq default pass / broker, Rust AMQP | yes | Compose error | Compose error | `<secret>` | L63 |
| `RABBITMQ_DEFAULT_VHOST` | rabbitmq default vhost / broker, Rust AMQP | no | default | default | `relay` | L64 |
| `POSTGRES_USER` | PostgreSQL connection and initialization / database and backend | no | default | default | `change_me` | L67 |
| `POSTGRES_PASSWORD` | PostgreSQL connection and initialization / database and backend | no | default | default | `<secret>` | L68 |
| `POSTGRES_DB` | PostgreSQL connection and initialization / database and backend | no | default | default | `reliable_event_relay` | L69 |
| `POSTGRES_HOST` | PostgreSQL connection and initialization / database and backend | no | default | default | `postgres` | L70 |
| `POSTGRES_PORT` | Network port / Compose and corresponding service | no | default | default | `5432` | L71 |
| `HOST_HTTP_PORT` | Network port / Compose and corresponding service | no | default | default | `8080` | L80 |

## Rust validation and relationships

Outside Compose, absence uses source defaults; empty is not absence. Missing `APP_ENV` uses development, empty fails. Missing `HTTP_ADDR` uses 0.0.0.0:8080, empty fails socket parsing. Missing `RUST_LOG` uses info; empty is retained for tracing filter resolution (final outcome unverified). Numeric `RELAY_*` and `CONSUMER_*` settings use the table defaults when absent; empty fails parsing. Limits must be positive; prefetch ≤32, pool ≤16; drain < shutdown. `RELAY_LEASE_MS` ≤3600000; timing-specific bounds are in source. Consumer names and topology are validated; empty is not an intentionally valid configuration. Source and quarantine exchanges and queues must differ.

`RABBITMQ_DEFAULT_USER` and `RABBITMQ_DEFAULT_PASS` are required and nonempty; missing host uses rabbitmq, missing port uses 5672, missing vhost uses relay. Empty/nonnumeric/zero port fails. Empty vhost is retained as a URI segment; broker access depends on broker state. Exchange/queue/routing names use table defaults when absent and undergo Topology validation. Missing AMQP timeouts use 10000 ms; empty fails parsing.

`POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` are required by workers, demo and replay; empty fails validation. Workers default host/port to postgres/5432; demo requires both explicitly. Empty/missing `REPLAY_OPERATORS` intentionally disables privileged routes; populated values require valid credentials and DB access. Empty/missing `RELAY_MAINTENANCE_CANDIDATES` disables targeted maintenance; populated accepts at most 32 unique UUID:cycle:revision entries (4096 bytes maximum). Never publish operator credentials.

Missing `HTTP_METRICS_ADDR`, `RELAY_METRICS_ADDR` and `CONSUMER_METRICS_ADDR` use 127.0.0.1:9100, 127.0.0.1:9101 and 127.0.0.1:9102 respectively directly; Compose supplies the table addresses. Empty or nonloopback addresses fail; all must differ from each other and HTTP. `DEMO_ENABLED` enables demo only for exact string true; empty/missing disables it directly, while Compose fixes true. `DEMO_TOKEN` and `DEMO_ORIGIN` are required nonempty with demo enabled; token is a runtime secret. start-local generates a token when needed without exposing it as a public frontend variable. Optional display inputs `DEMO_DB_PORT` and `DEMO_MANAGEMENT_PORT` default when absent to 5433/15672; empty is displayed without fallback. They do not configure Rust connection ports.

- [backend/src/config.rs](../../../../../../../rust-event-relay/backend/src/config.rs)
- [backend/src/main.rs](../../../../../../../rust-event-relay/backend/src/main.rs)
- [backend/src/infrastructure/rabbitmq.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/rabbitmq.rs)
- [backend/src/infrastructure/rabbitmq/consumer.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/rabbitmq/consumer.rs)
- [backend/src/telemetry/metrics.rs](../../../../../../../rust-event-relay/backend/src/telemetry/metrics.rs)
- [backend/src/infrastructure/demo_http.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/demo_http.rs)
- [scripts/start-local.py](../../../../../../../rust-event-relay/scripts/start-local.py)
