# url-shortener — Technical FAQ

[Project index](../index.md) · [Português brasileiro](../../pt-BR/faq/index.md)

Technical questions, detailed answers and follow-ups are available directly on this page. Historical milestone statements retain their dates; current corrections below take precedence. First-person examples describe portfolio artifacts, not employment experience. The [study guide](study-guide.md) retains its existing URLs and anchors for compatibility.

## Current source review — 2026-10-19

The answers below were checked against selected current source and test definitions. No sibling application tests or services were executed. See the [scope and evidence record](../operations/documentation-audit-2026-10-19.md).

### Q006 — What happens if the Redis counter disappears after a process initialized it?

**Answer:** `RedisIdGenerator` remembers `_initialized` locally. Its lock protects the initial SET NX in that instance, not counter durability. If the key disappears afterward, the next INCR can recreate it from zero, and the instance does not restore `URL_ID_START`. Reused IDs can target existing Cassandra primary keys; the adapter uses ordinary INSERT/upsert rather than a conditional uniqueness transaction. Redis INCR atomicity therefore does not prove permanent global uniqueness after data loss. A Cassandra timeout can also leave an already written mapping whose acknowledgement was lost; retrying POST normally allocates another ID. Counter recovery, cross-store reconciliation and a durable creation-idempotency contract remain separate design work, not capabilities delivered by the initialization lock.

### Q007 — Can changing only injected service settings safely rotate the public-code mapping?

**Answer:** No. The service receives Settings for constructing the public URL, but Base62 and obfuscation helpers independently call cached global `get_settings()`. Changing an injected instance does not necessarily change those helpers. Public codes use a reversible affine permutation modulo `62**7`, with SHA-256-derived parameters and literal `0` left-padding; the latter assumes a zero-first alphabet for correct round trips. Changing key/alphabet changes decoding of existing links, with no version marker or migration registry. This is obfuscation, not encryption or authorization. An actual rotation would need explicit compatibility/versioning and recovery requirements; no rotation or real-store recovery was executed. Fake-backed tests demonstrate selected call/error contracts, not historical-code compatibility across every configuration.


## URL Shortener technical interview study guide


[English](index.md) | [Português brasileiro](../../pt-BR/faq/index.md)

Study the problem, choices, alternatives, trade-offs and production limitations rather than memorizing answers. First-person wording should reflect experience you can substantiate. Repeated explanations from the original notes are consolidated; literal examples remain in the appendix. Paths/commands refer to the `url-shortener` repository.

Code review corrections: Redis counter initialization is lazy on first ID generation, not in lifespan. Lifespan issues Cassandra CREATE TABLE IF NOT EXISTS; Compose bootstrap can create/alter roles/keyspace. Startup is a write operation, not a harmless check against existing data. There is no TTL, deduplication or conditional-insert protection against ID reuse. Configuration errors can become 500, distinct from infrastructure 503; invalid payloads produce 422. No explicit QUORUM level is selected in the current execution profile; QUORUM discussion below is a hypothetical design choice.

## 1 Overview

The project is a Python/FastAPI URL shortener for backend engineering and system-design learning. Authenticated creation validates a URL, allocates an integer via Redis INCR, encodes Base62, applies reversible obfuscation to form a seven-character code, and persists integer-to-URL mapping in Cassandra. Public resolution reverses the transform, decodes the integer, queries Cassandra and returns 301 Moved Permanently. Local Docker infrastructure includes Redis and three Cassandra nodes.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The request path makes responsibility testable: HTTP validates/authenticates, a service coordinates allocation and storage, and adapters encapsulate protocol calls. Resolution reverses representation rather than searching by public text. This saves a stored code key but couples old links to alphabet/key compatibility. Follow-up: Is this a multi-service ecosystem? No; Redis/Cassandra are dependencies of this one independent application, with no verified portfolio partner.

## 2 Why this problem

A small API exposes meaningful questions about unique IDs, concurrency, persistence, compact representations, distribution, durability, availability, HTTP caching and redirects. The goal is a system whose entire flow and trade-offs can be understood, not technology quantity.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A tiny external contract can still expose distributed failure: allocation may succeed while mapping fails, and a timeout may hide a successful write. This makes the project useful for explaining boundaries without inventing scale. A single SQL database would reduce operational and transactional complexity for a small product. Follow-up: What is demonstrated rather than intended? Source paths and fake-test assertions demonstrate local mechanisms; production volume, HA and recovery are not demonstrated.

## 3 Components

FastAPI handles HTTP; Redis allocates IDs; Cassandra persists mappings; Base62 represents integers; reversible transformation hides the obvious sequence; Compose reproduces local infrastructure; Pytest tests behavior. Cassandra is peer-to-peer: cassandra-1 is a discovery seed, not a leader/master.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Each component contributes a different guarantee: Pydantic validates payload syntax, Redis serializes a counter increment, Cassandra stores a key lookup and the affine map supplies reversibility. None supplies authorization for redirects or a transaction across stores. An implementation with one datastore could combine identity/mapping atomically. Follow-up: Does choosing distributed components prove distributed resilience? No; the three local peers share a host and the allocator has no failover.

## 4 Python FastAPI and architecture

Python was deliberate hands-on learning in another backend ecosystem. Work mainly coordinates validation and infrastructure rather than heavy compute. Transferable engineering reasoning is distinct from new language/framework syntax. FastAPI provides HTTP, data validation and OpenAPI while route → controller → service → infrastructure keeps responsibilities visible. This is pragmatic layering, not a complete rigid Clean Architecture implementation; more interfaces/repositories need actual benefits.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The current routes and dependency clients are synchronous, so blocking calls can occupy request worker capacity even though FastAPI supports async handlers. Layering does not automatically invert dependencies: the service imports concrete adapter types. Ports or async drivers would be hypothetical changes with contract/connection-lifecycle costs. Follow-up: Would merely changing def to async def improve it? No; synchronous I/O inside an async handler can block the event loop unless deliberately offloaded.

## 5 Creation flow

POST /urls → Basic Auth → URL validation → Redis INCR → integer → Base62 → reversible obfuscation → seven-character code → Cassandra persistence → 201 Created. Creation changes state, so it is authenticated. Each valid POST allocates another ID; no original-URL deduplication or TTL is implemented.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The response is built after store_url returns; no transaction spans the earlier increment. Repeated valid requests therefore create separate codes, and timeout recovery does not have a durable request identity. A request-key/result record could implement idempotency, but needs concurrency/conflict/expiry rules. Follow-up: Can a failed 503 creation have left a mapping? Yes, if Cassandra accepted the write before the response was lost; failure response is not proof of no effect.

## 6 Redis responsibility

Redis is the atomic ID allocator, not the mapping database, GET cache or message queue. INCR handles concurrent increments. SELECT MAX(id)+1 would race when two requests observe the same maximum and is not the intended Cassandra global-counter model. Atomicity does not require manually queueing requests.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** INCR guarantees serialized modification of one Redis key, not durable uniqueness after every recovery scenario. Once initialized, the generator caches that fact, so deleting the key can cause a later INCR to restart without restoring the configured floor. A datastore-owned identity would avoid separate allocator recovery but change the exercise. Follow-up: Is the Python Lock the cross-process guarantee? No; server-side NX/INCR provide that coordination during healthy operation.

## 7 Counter initialization

Default first intended ID is `62^4 = 14,776,336`. SET with NX initializes the counter to 14,776,335 only if absent; the first INCR returns 14,776,336. Existing persisted state is not overwritten by initialization. This happens lazily on first generation, with a local lock around initialization.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The local lock prevents duplicate initialization calls within one generator, while NX prevents competing processes overwriting an existing counter. Initialization is lazy, so constructor/lifespan success does not prove the first increment will work. A startup check could fail earlier but would add startup dependency behavior and still not coordinate restored mappings. Follow-up: Can setting a new URL_ID_START move an existing counter upward? No; NX leaves existing state unchanged.

## 8 Why start at that value

With the chosen alphabet, 62^4 encodes as `10000`, selecting a desired Base62 range before transformation. This is a project choice, not a fundamental shortener requirement.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The configured lower bound chooses a representation range; fixed seven-character output actually comes from obfuscation/padding, not this start value. Starting higher consumes part of the finite domain and does not improve randomness or security. A zero-based counter or random stored code would have different readability/collision trade-offs. Follow-up: What happens at 62**7? Obfuscation rejects out-of-domain input after allocation; no automatic expansion/versioned code format is implemented.

## 9 Redis durability and availability

AOF with appendfsync everysec improves restart recovery but does not implement failover. There is one Redis, no Sentinel/Cluster. Redis failure blocks new creation with infrastructure error; durability is different from HA.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The configured everysec policy trades flush cost against a potential recent-write loss window. A surviving Cassandra row plus a regressed counter is more serious than a harmless gap because INSERT can overwrite by reused ID. Replication/Sentinel could improve allocator availability, but recovery consistency still needs design. Follow-up: Would stronger fsync alone solve every failure? No; it does not prevent manual reset, incoherent backup restoration or total storage loss.

## 10 Partial failures across two stores

Redis allocation precedes Cassandra persistence without a shared transaction. If persistence fails, a sequence gap is acceptable: uniqueness matters, gaplessness does not. If Redis loses acknowledged increments but Cassandra retains their mappings, IDs can be reused. Cassandra's ordinary insert can replace a mapping, making this a correctness risk. AOF reduces risk without fully solving recovery; production ID guarantees need review.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The service wraps adapter failures but implements no compensating write, distributed commit or reconciliation. Reclaiming failed IDs is unsafe if storage acceptance was uncertain; tolerating gaps is simpler than guessing. A single-store transaction could simplify correctness. Follow-up: Why is a timeout not rollback? The server may finish while the acknowledgement is lost. A safe retry policy must account for the possible original effect and cannot infer it from 503 alone.

## 11 Base62

Alphabet: `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. It compactly represents integers using URL-friendly alphanumerics. Encode/decode returns the same integer. It is neither encryption nor Base64 and offers no confidentiality.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Encoding repeatedly divides by 62; decoding accumulates value*62+digit. Representation length grows logarithmically with the integer, while this public format fixes width through another transformation. The alphabet must have 62 unique characters. A lookup map could replace alphabet.index for decoding, though codes are short and no measured bottleneck exists. Follow-up: Is any custom alphabet safely supported end to end? Not established: obfuscation pads literal 0 rather than the configured zero digit.

## 12 Obfuscation and code space

Plain Base62 exposes sequential progression. A reversible transform hides the obvious sequence and yields fixed seven-character codes; it is not strong cryptography. A cryptographic requirement needs an appropriate reviewed construction. `62^7 = 3,521,614,606,208` possible codes is a mathematical domain, not measured capacity for trillions of stored URLs.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The map is (a*x+b) modulo 62**7. Choosing gcd(a,modulus)=1 permits a modular inverse and gives one-to-one mapping within the domain for fixed settings. SHA-256 derives a/b but does not make this affine construction authenticated encryption. Random stored codes remove reversible-key coupling but require collision handling. Follow-up: Can existing links survive arbitrary key rotation? No; a new inverse produces different lookup IDs without versioning/migration.

## 13 Cassandra versus a simpler database

Known integer → primary-key lookup → original URL fits query-driven modeling. Cassandra supports study of replication, peers, seeds and coordinators. It is not mandatory for a small shortener; PostgreSQL could be operationally simpler. Distinguish the simplest small-product design from a technology selected for explicit distributed-storage learning.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The table matches a known-ID lookup but Cassandra adds nodes, replication/authentication and operational tuning beyond the HTTP contract. The selected stack is evidence of a study design, not proof it was required by measured load. SQL with a generated ID could combine allocation and mapping. Follow-up: What access pattern would need another table? Lookup/deduplication by original URL cannot efficiently use the current ID-only schema without a new query-oriented model.

## 14 Data model

```sql
CREATE TABLE urls_by_id (
    id bigint PRIMARY KEY,
    original_url text
);
```

Resolution needs no joins. Public code is not the primary key because it reversibly maps through Base62 back to the integer. Persistence keeps that integer identity independent of its public representation.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The bigint partition key makes equality lookup direct; parameters carry ID and URL rather than interpolating user values. INSERT is an upsert, not a conditional collision check, and there is no TTL or stored public-code version. Query simplicity trades away original-URL search and edit history. Follow-up: Why is upsert dangerous after allocator loss? Reusing an existing ID can change the old code destination, even though the application exposes no explicit edit route.

## 15 Seeds coordinators and replicas

No permanent leader exists. cassandra-1/2/3 are peers. Seed means bootstrap discovery; coordinator means the node managing one request; replica means a node storing a copy. Another request can have another coordinator. None of these roles should be described as a permanent leader.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The driver chooses coordinators using its execution/load-balancing policy; replication strategy determines owners for a partition. Naming cassandra-1 as seed changes discovery, not leadership or all-write routing. A SQL primary/replica analogy can therefore mislead. Follow-up: Can a healthy seed prove all replica data is readable? No; request consistency, replica reachability and client topology determine that boundary. Real outage schedules were not tested in this review.

## 16 Replication factor

NetworkTopologyStrategy with RF=3 in datacenter1 replicates rows among the three local nodes. This alone is not end-to-end HA: consistency levels, client availability, topology, deployment, failure detection and operations matter. All three development containers share one physical machine and fail with that host.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Copies are distributed according to the configured datacenter strategy, while consistency settings determine acknowledgements per operation. Adding replicas can improve some failure tolerance but increases storage/repair/operation work. Same-host development does not establish zone resilience. Follow-up: Is RF=3 a read-after-write guarantee? No; the execution profile leaves read/write consistency implicit, so RF alone does not define the client-visible promise.

## 17 Consistency levels

Choose per-operation read/write guarantees after defining failure, latency and availability requirements. With RF=3, QUORUM is one option, not automatically best. Current driver execution profile does not explicitly choose QUORUM; the study discussion is a proposed review rather than implemented configuration.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Read/write quorum overlap is useful theory, but requires precise replica sets and policies and does not automatically eliminate concurrent-write conflict semantics. Stronger acknowledgement requirements can reduce availability when too few replicas respond. The current code chooses DC-aware routing without owning an explicit consistency contract. Follow-up: What should documentation state today? RF/topology and the missing explicit policy, not an invented QUORUM configuration or measured latency.

## 18 Resolution flow

GET /{short_code} → validate/reverse obfuscation → Base62 decode → integer → Cassandra lookup → original URL → 301. It is public so shared links do not require recipients to authenticate.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The fixed code length/character validation happens during reverse transformation, then Cassandra supplies the destination. Redis is not queried on this path; changing the obfuscation settings can nevertheless break old lookup results. A stored-code lookup would move compatibility into data instead. Follow-up: What if the code is well-formed but absent? It shares the public 404 response with malformed codes; configuration/adapter failures remain 500/503.

## 19 Permanent redirects

301 matches permanent mapping semantics and may be cached by browsers/proxies, reducing future backend requests. That benefit also means editing a server mapping may not update clients with cached old destinations. Mappings are effectively immutable in the application; there is no edit endpoint. A temporary redirect such as 302 merits review for mutable destinations or request-level analytics. Cache behavior varies and is not a capacity guarantee.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The response encodes the chosen HTTP permanence semantics; clients can retain Location and bypass later lookups. This benefits repeated resolution while reducing server visibility and making future destination changes surprising. A 302/307 policy would have different caching/method implications and needs a new contract. Follow-up: Can logs count every click? No. Cached redirects may never reach this server, so analytics would need explicitly defined accuracy limits.

## 20 Why no Redis GET cache

Redis currently has one clear responsibility. Resolution caching would add invalidation, eviction, memory, misses, consistency and failure behavior. Introduce it when read measurements or an explicit study requirement justify it, not merely because Redis exists.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** An immutable mapping cache could be read-through by code/ID, but cache misses still need Cassandra and cached 404s require special freshness handling after creation. Memory limits, eviction and fallback behavior matter even without destination edits. None is implemented. Follow-up: Does using Redis for allocation justify storing mappings there too? It is a separate responsibility and recovery dependency; introduce it only with a requirement, not because the client is already available.

## 21 Why no broker

Creation returns the code immediately through a short synchronous flow. Kafka/RabbitMQ would add producers, consumers, retries, idempotency, delivery and eventual consistency without a current requirement. Analytics/auditing/post-processing or decoupled integrations could justify asynchronous work later.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Moving persistence behind a queue would change 201 semantics: returning before mapping exists could produce immediately unresolvable links unless another durable acceptance contract were designed. A broker also needs duplicate handling and consumer failure recovery. Follow-up: Could analytics be decoupled instead? Hypothetically yes, if redirect latency and acceptable event loss/replay are specified. That would be a new flow; the independent Rust Relay is not currently its producer/consumer partner.

## 22 Why one service

The small domain lacks independent contexts or operation needs requiring separate deployments. A modular service is easier to run/test/explain. Microservices would introduce communication, observability, retry and partial-failure costs before a corresponding requirement.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** One process boundary keeps synchronous creation and error translation easy to trace. Splitting allocator/storage HTTP services would add transport timeouts and deployment coordination without fixing the existing Redis/Cassandra atomicity gap. Modular code can still be testable without independent deployment. Follow-up: What would justify a split? A verified independent scaling, ownership or isolation requirement with a contract and measurements; no such portfolio runtime integration is currently evidenced.

## 23 Basic Authentication

Basic Auth protects POST while GET remains public, keeping identity outside the main study scope. Credentials are transport-encoded rather than protected by encryption; production requires HTTPS. `secrets.compare_digest` supports comparison, and real credentials must not be committed. Multiuser product identity could need tokens or an identity provider; Basic Auth here is not that complete architecture.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The implementation compares UTF-8 credential bytes with secrets.compare_digest and returns a Basic challenge for invalid credentials. Missing configured credentials produce a server configuration error. This avoids ordinary direct equality timing behavior but does not rate-limit guesses or manage users. Follow-up: Does public GET authenticate the destination owner? No; it simply resolves a shareable mapping. Product authorization and abuse moderation are separate future requirements.

## 24 Secrets

`.env.example` is public configuration structure; real Redis/Cassandra passwords, Basic Auth credentials and OBFUSCATING_KEY belong in ignored local configuration or appropriate infrastructure secret storage. Production secret management is a separate concern.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Ignored files protect against ordinary source inclusion but are not encrypted storage or rotation policy. The key has a data-compatibility role as well as confidentiality concerns: losing/changing it breaks existing decoding. A secret-manager rollout would need access control and versioning rather than merely moving values. Follow-up: Were live secrets inspected here? No. Only safe code/configuration metadata and documentation were used; no credential values or database content were read.

## 25 Connection lifecycle

FastAPI lifespan constructs Redis, ID generator and Cassandra cluster/session for reuse, closing resources on shutdown. Per-request Cassandra sessions would be costly. Lifespan also initializes the URL table, so startup can write schema even before HTTP writes.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Cassandra cluster/session creation precedes serving and failed connection creation shuts down the cluster. The finally block closes initialized Cassandra resources and Redis. Reuse amortizes connection setup but ties app lifecycle to startup availability. Redis counter initialization remains lazy. Follow-up: Can health startup be treated as read-only? No; table initialization issues DDL. Strong production least-privilege design could move schema work into migrations, a hypothetical change.

## 26 Docker-first operation

Docker/Compose, an editor and Git reproduce Python/Redis/three Cassandra nodes without installing each runtime on the host. Three same-host Cassandra containers demonstrate logical cluster topology, peers and replication, not independent physical failure domains or production HA.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Compose controls service names, dependency gates, bind storage and a bridge network. The application uses container DNS names, while loopback-published ports are for host access. Local reload and source binds help development, not immutable release rollout. Follow-up: Does rebuilding an image change initialized database credentials? Not automatically; retained data/configuration identity must be handled deliberately. A production deployment would need artifact, TLS, recovery and readiness policy beyond this local setup.

## 27 Readiness

Compose health checks and dependency conditions express readiness instead of arbitrary sleeps. Service startup time varies. Application health queries OpenAPI and is not a full production dependency/observability guarantee. Startup hooks must be reviewed for schema and role writes before using an existing database.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Infrastructure checks can gate startup but do not freeze dependency health afterward. The app probe only requests OpenAPI; it does not run a fresh counter increment or mapping lookup. A more precise readiness design could include bounded read-only dependency probes, without allocating IDs simply to test health. Follow-up: Is Redis optional during Compose startup because GET skips it? No; service dependency conditions and request dependency paths are separate contracts.

## 28 Tests

Pytest covers HTTP authentication/redirects, creation/resolution, Redis allocation behavior, Cassandra store behavior, Base62 and reversible transforms. The standard suite uses fakes. These deterministic tests establish application contracts, not all real-cluster behavior. Infrastructure integration needs separate isolated validation.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The fakes model responses and errors so tests can assert controller status, transformation round-trips and service call ordering cheaply. They do not reproduce driver retry/default consistency or replication. Real-service tests would need disposable stores and controlled fault schedules. Follow-up: Is a checked-in suite a new passing result? No; no application test ran in this review. Preserve dated historical execution separately from current test inventory and future gaps.

## 29 Why fakes

Encoding, input validation, authentication and service behavior do not need three database nodes per case. Separate logic correctness from real-driver/cluster integration; each has value and a different cost.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Dependency injection at lifecycle/route boundaries permits tests to supply generators/stores with deterministic outcomes. This is useful for proving no storage call follows invalid input or for simulating adapter failure, but a fake cannot prove network authentication or actual atomicity. Follow-up: What makes an integration test meaningful? Assert a required contract using isolated real infrastructure and controlled cleanup; do not point fixture deletion at an existing application database.

## 30 Dependency failures

Persistence/lookup failures map to sanitized 503 without hostnames, traces or credentials. Redis failure blocks POST; GET resolution itself needs only Cassandra. Configuration faults are distinct and can map to 500.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Error translation keeps dependency details out of public responses while preserving exception causes internally. Different failure categories should not all be retried: configuration requires repair, and uncertain storage effects need reconciliation. Client sanitization does not automatically sanitize logs. Follow-up: Would returning 404 for Cassandra outage be acceptable? No; it would falsely describe unavailable evidence as an absent mapping. The implemented 503 distinguishes inability to look up from not-found.

## 31 Availability per operation

For an already-running app with Cassandra healthy, Redis failure can block creation while existing links still resolve. Startup has stronger dependency gates, so do not confuse this read-path property with an app that always starts without Redis.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Availability must be discussed per operation and lifecycle phase. GET does not increment Redis but both paths use Cassandra; a cold start initializes Cassandra schema and Compose waits for dependencies. A single overall uptime label hides those differences. Follow-up: Can cached 301 links still work during complete application outage? Some clients can reuse cached destinations, but that is client behavior, not a guaranteed service failover mechanism or measured availability claim.

## 32 Invalid URLs

FastAPI/Pydantic validates the HTTP payload before ID allocation/persistence. Invalid payloads return 422 and avoid unnecessary infrastructure work.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** HttpUrl accepts syntactically valid HTTP/HTTPS destinations, including ones that may later be unreachable or abusive. The application stores and redirects without fetching them. A reputation/allowlist feature would add false-positive/freshness/operations costs; a future preview fetch would create a new SSRF boundary. Follow-up: Does rejecting malformed URL stop malicious links? No; valid syntax is not reputation, ownership or content safety.

## 33 Invalid codes

Malformed and unknown codes return 404; the public API does not reveal whether decoding, deobfuscation or missing mapping caused the result. Configuration/infrastructure faults are handled separately.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The service reverses a seven-character code and validates its alphabet before Cassandra lookup. Invalid/absent identities deliberately share a public not-found contract. Configuration errors are not user errors and infrastructure outage is not absence. Follow-up: Does hiding the specific 404 reason stop enumeration? It limits detail but public mappings remain discoverable; there is no rate limiter or confidentiality guarantee, and the affine transform is not secure encryption.

## 34 Repeated URLs

Two valid posts of the same URL allocate two IDs. Deduplication would require another lookup/index/mapping by original URL and concurrency rules. The current simple write path does not implement it.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Deduplicating by URL would also need normalization rules: differently written URLs can have different semantics, and query parameters may be significant. Concurrent creates need an atomic identity policy rather than a check-then-insert race. Follow-up: Would a Cassandra secondary index alone deliver idempotency? No; lookup support does not define concurrent arbitration, payload conflict or stable replay results. Current repeated POST behavior remains intentionally distinct allocation.

## 35 Expiration

No TTL or automatic expiry. Permanent mappings avoid retention/cleanup/expired-response/cache decisions; adding expiry would introduce those requirements.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A TTL would remove mappings but not necessarily invalidate client-cached permanent redirects. It also introduces expiry versus unknown responses, clock/retention policy and eventual cleanup behavior. A temporary redirect policy might better match expiring links. Follow-up: Does the Redis counter need TTL to match mapping retention? No; reusing expired IDs is dangerous while old codes/caches can survive. Identity lifecycle must be designed separately from row retention.

## 36 Scale claims

Atomic allocation and distributed storage permit scalability discussion, not a claim of billions of requests or measured production throughput. Define hardware, topology, consistency, load, latency and throughput before claiming capacity. “High-throughput” describes the study objective, not a demonstrated metric.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Code-space cardinality, storage capacity and request throughput are different quantities. The first is arithmetic; the other two depend on data size, topology, consistency and workload. Current synchronous dependency calls and one counter suggest concrete measurement targets. Follow-up: How would you report a future load test? State versions/hardware/input/concurrency, latency distribution, throughput/error rate and limits; do not extrapolate universal scale or equate passing unit tests with capacity.

## 37 Potential bottleneck

A single global Redis allocator centralizes writes and is a single point of unavailability. Efficient INCR does not remove central dependence; higher availability/volume may justify another allocation design.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The allocator adds one synchronous network operation to every create and central state to recover. Cassandra latency and request-thread capacity can also dominate, so no bottleneck ranking is measured here. Block allocation could reduce counter calls but wastes ranges after crashes and complicates ownership. Follow-up: Does GET share the allocator bottleneck? Its source path does not use Redis; resolve and create should be measured separately.

## 38 ID alternatives

UUID, UUIDv7, Snowflake-like IDs, preallocated blocks, dedicated allocation service or random IDs with collision handling each have trade-offs. Redis INCR is deterministic and easy to explain under concurrency but centralizes allocation.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Evaluate collision risk, code length, central state, ordering and failure recovery rather than choosing a fashionable ID. UUID/random generation shifts uniqueness assumptions; Snowflake-like designs require node identity and clock handling; blocks reduce allocation traffic with crash gaps. Follow-up: Would an alternative ID alone solve HTTP retries? No. Request idempotency still needs stable logical-operation identity and stored result/conflict policy, distinct from generating a fresh unique row ID.

## 39 Why not UUID

UUID could reduce dependence on a central counter. This project specifically studies integer → Base62 → public-code transformation and atomic allocation. Different requirements could make UUID an appropriate choice.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** UUID would occupy more bits than this seven-digit domain if encoded directly, so public-code requirements need deliberate redesign. Truncating a UUID creates collisions; hashing does not guarantee uniqueness. A separately stored random short code could preserve public length with conditional insertion/retry. Follow-up: Does UUIDv7 order requests exactly? It improves time-oriented representation but is not a global business or acceptance ordering guarantee.

## 40 Observability

There is no complete production metrics/tracing/alerting stack. Potential production additions include latency/error rates, dependency availability, traces and alerts. These are limitations/future considerations, not current capabilities.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Useful telemetry would distinguish create/resolve, validation/configuration/store errors, dependency timeouts and counter recovery risk. Structured dimensions should avoid unbounded code/URL labels and credentials. Trace IDs are not proof a mapping was durably committed. Follow-up: Is OpenAPI probe a metrics system? No; it provides a narrow serving signal. Dashboards/alerts/tracing and their retention remain hypothetical operational work, not implied by framework support.

## 41 CI and deployment

Describe only checked-in workflows. Local Docker/test reproducibility does not automatically provide CI/CD, production orchestration or deployment automation.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The local Compose command uses reload and bind mounts; it is a development lifecycle. A release would need immutable artifacts, compatible config/code mapping, schema/bootstrap review and rollback/recovery checks. Follow-up: Does automated test configuration equal successful deployment? No. Workflow files describe intended checks; actual results need dated executions. No remote CI, release or network action occurred here, and owner-managed GitHub names/URLs were not assumed changed.

## 42 Kubernetes

Compose meets local development/study needs. Kubernetes would add operational scope unless distributed deployment itself becomes an explicit learning/product requirement.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** An orchestrator can schedule/restart workloads but does not repair regressed allocator state or ensure Cassandra consistency. Stateful deployment would still require storage, failure domains, backup, credentials and recovery design. Moving this learning setup into Kubernetes could hide the original correctness problem under operational complexity. Follow-up: What would justify it? A separate explicit orchestration goal and tested requirements, not simply three database containers or a production-ready label.

## 43 A startup product choice

For a small new product, PostgreSQL is a strong simple/mature/flexible option. Start from actual requirements and observed scale. Cassandra's learning and key-lookup fit does not establish universal superiority.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A single relational transaction could insert a mapping with database-generated identity and avoid the Redis/Cassandra dual-write boundary. Indexes support lookup and uniqueness with simpler local deployment. That option trades away this exercise in peer replication and allocator separation; no comparative benchmark favors either stack here. Follow-up: Should the portfolio be rewritten now? Not in this documentation-only scope. Explain the alternative and requirements before authorizing implementation work.

## 44 SQL and NoSQL

Either can support shorteners. Access patterns, consistency, scale, operations, team and infrastructure determine suitability; SQL is not incapable of this model.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Relational constraints/transactions and query-shaped distributed tables expose different modeling/operation costs, not a universal winner. This actual mapping is a single key/value access pattern, while future URL deduplication/analytics could change queries. Follow-up: Is NoSQL automatically faster? No. Hardware, replication, consistency, workload and implementation dominate measured outcomes. Explain the current primary-key query and cross-store correctness costs instead of claiming technology-based capacity.

## 45 Production review

Evaluate ID allocator HA/recovery, Cassandra consistency and independent failure domains, TLS, product authentication, secret management, rate limiting, observability/alerts, load and real integration tests, backup/recovery, CI/CD and malicious-URL abuse prevention. Select improvements from actual requirements rather than adding all technologies unconditionally.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Start with correctness requirements: never reuse a mapped ID, preserve decoding compatibility and distinguish unavailable from not-found. Then define acceptable durability/availability and abuse exposure. Adding caches or nodes before these contracts can make recovery harder. Follow-up: Which checks are already complete? Source/fake-test behavior and local documented topology; real loss/recovery, independent failover, public TLS and production rollback remain gaps rather than silently completed checklist items.

## 46 Most interesting decision

Separating identity allocation from persistence clarifies responsibility but creates a distributed partial-failure problem without one transaction. Gaps, state loss and ID reuse are central learning points.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The service ordering makes the trade-off visible: Redis owns allocation, Cassandra owns mapping, and no local transaction can cover both. This is a learning interpretation, not an invented historical evaluation of competing designs. Follow-up: What invariant matters most? No allocated ID may overwrite another logical mapping after recovery. Sequence gaps are acceptable; reuse is not. Explain how lost counter state violates that invariant despite healthy atomic increments.

## 47 Greatest limitation

One Redis with AOF still lacks failover and can lose allocator state while Cassandra retains higher-ID mappings. Recognize correctness and recovery limitations explicitly rather than claiming persistence solves them.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The operational risk is also a data-integrity risk: one regressed counter can target IDs that Cassandra still holds. The service uses ordinary upserts and has no recovery guard against this mismatch. Stronger persistence, unique conditional storage or one-store allocation are alternatives with different costs. Follow-up: Can three Cassandra replicas protect the allocator? No; they preserve mappings, not Redis state, and may actually preserve rows that a lost allocator later overwrites.

## 48 Lessons

Persistence differs from HA; replication from backup; seed/coordinator from leader; Base62/obfuscation from encryption; atomicity from queues; containers from production infrastructure; fakes from real integration; potentially scalable design from measured throughput.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** These distinctions can be defended by tracing one successful request and then changing one failure assumption at a time: lost Redis state, unavailable Cassandra, changed key or cached redirect. General concepts become meaningful when tied to observable code. Follow-up: What is a limitation rather than a lesson learned in production? All unmeasured capacity and unexecuted recovery cases remain study limits; no user incidents or professional outcomes should be invented.

## 49 Honest experience

This project broadens hands-on Python/Cassandra/distributed-systems understanding; do not pretend prior professional mastery. Explain actual connection lifecycle, concurrency, persistence, replication, failures and tests separately from professional experience.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A strong answer can demonstrate implementation understanding without claiming professional deployment: locate INCR/NX, explain affine inversion, show store calls and identify failure mapping. Suggested first-person text is rehearsal material, not a verified résumé statement. Follow-up: What if asked for production traffic or outcomes? State that no such measurements/evidence are in this repository. Discuss how you would validate a requirement as hypothetical work rather than manufacture an achievement.

## 50 Learning a new technology

Start with its responsibility and required guarantees, then study ecosystem implementation. Cassandra understanding includes peers, seeds, coordinators, RF and operational consistency, not simply connecting a driver. This reasoning transfers between stacks.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Separate language learning from engineering invariants. Python/FastAPI syntax differs from other stacks, but response ambiguity, resource ownership and atomicity boundaries persist. Use small fixtures to test representation and service ordering before isolated real-driver tests. Follow-up: Would reading framework documentation alone prove understanding? No. Trace lifecycle cleanup and a failing request, then explain what fake tests leave unverified. Do not claim an unrecorded personal learning timeline.

## 51 Layer responsibilities

Route defines HTTP/dependencies; controller bridges transport/application; service coordinates creation/resolution; infrastructure encapsulates Redis/Cassandra. FastAPI permits inline logic, but visible responsibilities improve comprehension without unnecessary extra layers.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Controllers translate configuration/infrastructure/not-found categories into HTTP status, while service logic retains transform and call ordering. Adapters wrap protocol errors but do not decide public redirect semantics. This keeps transport-specific responses out of the persistence operation. Follow-up: Is the service fully independent? No; it imports concrete Redis/Cassandra adapters and settings. A port could improve decoupling, but would need a stable behavioral contract rather than generic methods without guarantees.

## 52 SOLID

Pragmatic separate responsibilities and replaceable dependencies improve testing. Do not present the project as a formal demonstration of all five principles or invent interfaces/hierarchies to satisfy a checklist.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Single responsibility is visible in allocation versus mapping, but separation can also create partial failures; principle names do not prove a better system. Dependency replacement for tests is useful even with concrete imports. Follow-up: What would overengineering look like? Generic CRUD/repository hierarchies, extra services or interfaces that simply forward one method without protecting a meaningful seam. Explain a real invariant/error boundary before invoking a design-principle acronym.

## 53 Repository abstractions

CassandraUrlStore encapsulates required persistence. Multiple implementations, a richer domain or actual decoupling needs could justify a formal repository abstraction; avoid adding it everywhere by default.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The concrete store owns table initialization and parameterized insert/lookup. A useful abstraction would retain upsert/absence/error semantics; hiding them behind generic save/find can mislead retry reasoning. Follow-up: Could a SQL replacement be drop-in? Only if its contract matches identity, failure and lifecycle expectations, or the service changes deliberately. Transactional identity generation would be a redesigned orchestration boundary rather than a cosmetic adapter substitution.

## 54 Dependency injection

Construct resources in lifecycle instead of creating arbitrary infrastructure inside logic. Tests replace dependencies with fakes, permitting behavioral checks without real services per case.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Application state holds reusable resources created during lifespan; route dependencies supply the service rather than opening new clusters per call. Reuse reduces setup costs but requires closing resources and handling failed startup. Follow-up: Is dependency injection automatically a container framework? No; explicit construction and dependency functions provide the seam here. Fakes should match behavioral failure contracts, not merely share method names while hiding real uncertainty.

## 55 Internal error details

Infrastructure exceptions are not public contracts and can leak sensitive information. Return controlled client errors; a production logging/observability policy would retain appropriate diagnostics internally.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Typed adapter/service exceptions retain causes internally while controllers return controlled text. Configuration 500, infrastructure 503 and not-found 404 mean different repair/retry actions. A production logger must separately redact source details and sensitive destinations. Follow-up: Why not log every exception chain unconditionally? Causes can contain hosts, credentials or queries. Sanitized client output cannot protect an unrestricted diagnostic sink.

## 56 Scaling reads

Measure first. Popular-mapping caches or HTTP/edge caches could help when justified. Immutable mappings simplify caching, but invalidation, consistency, eviction and failure still need design.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Current GET uses one Cassandra lookup after local reversal. Caching can reduce store calls but not automatically preserve correctness under creation, expiry or future edits. A 301 cache already exists at the HTTP-client layer and cannot be controlled identically to a server cache. Follow-up: What should be measured before adding Redis cache? Resolve latency/error distribution and hit candidates under representative traffic, with explicit memory/fallback policy. No such measurements were performed here.

## 57 301 and capacity

Cached redirects can bypass later backend requests. Cache clearing/ignoring and varying clients prevent treating this as a guaranteed capacity solution. It complements, not replaces, planning and measurements.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** The request that first resolves still needs the service and Cassandra; later requests may be handled by client/intermediary cache. This shifts traffic rather than proving maximum backend throughput, and cache behavior varies with clients/settings. Follow-up: How does caching affect an outage experiment? A cached success can mask the outage, so test uncached clients separately from repeated cached resolution. Neither type of runtime experiment was executed in this review.

## 58 Editable destinations

Reconsider redirect semantics before introducing updates. A cached 301 can retain the old destination even after a database change. Mutable mappings need explicit update modeling and suitable temporary redirects/cache policy.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Although no edit API exists, ordinary Cassandra upserts mean allocator ID reuse could change a mapping accidentally. A future intentional edit must define ownership, authorization, consistency and cache freshness rather than just adding UPDATE. Follow-up: Would returning 302 invalidate an already cached 301? Not reliably for clients that no longer contact the service. Migration of old permanent links needs explicit compatibility/communication behavior.

## 59 Click analytics

Avoid making redirect depend on heavy synchronous analytics. Events/asynchronous processing may justify a broker only after defining acceptable loss, exactly-once expectations, volume and latency. Current code does not implement analytics.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A redirect log records only requests reaching the app, not visits served from cached 301. An event pipeline could persist observed clicks asynchronously, but needs stable event identity, retry/deduplication and an acceptable loss budget. Follow-up: Does the Rust project already provide that pipeline? No. It is independent and lacks its own worker/consumer composition; using it would require a new verified integration and cannot be implied by both projects being in this workspace.

## 60 Rate limiting

A real public API merits review of creation limits and abuse prevention. These are not currently implemented features.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Creation limits and redirect limits serve different purposes: write quotas constrain allocation/storage abuse, while public lookup limits must avoid breaking legitimate shared links. Identity/IP choices, distributed counters and fallback policy affect fairness. Follow-up: Would a Redis outage make a new limiter fail open or closed? That is a new design decision with availability/security trade-offs. Redis is currently only an allocator; no limiter policy is implemented or tested.

## 61 CAP discussion

Do not reduce CAP to choosing two letters or label Cassandra AP without operational detail. Under partition, availability/consistency decisions depend on read/write requirements, RF and consistency levels. Discuss concrete failure behavior.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** CAP addresses partition-time trade-offs under precise definitions, not normal-operation speed. A concrete Cassandra request may wait for a selected number of replicas and fail when too few are reachable; the current code does not select explicit levels. Follow-up: Why is assigning one permanent AP label inadequate? It hides per-operation policy and failure assumptions. The Redis allocator also imposes a separate creation dependency, so Cassandra classification alone cannot describe end-to-end availability.

## 62 Quorum arithmetic

With RF=3, quorum is `floor(RF / 2) + 1 = 2`. Arithmetic alone does not choose per-operation guarantees or account for latency/availability. This is a hypothetical setting rather than an explicit current profile configuration.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** With the same replica set, R=2 and W=2 overlap for N=3. The overlap supports reasoning but does not by itself define conflict timestamps, concurrent updates or a linearizable API. Waiting for more replicas trades response latency/availability against acknowledgement strength. Follow-up: Where is QUORUM configured in this code? It is not explicitly set in the execution profile. State the hypothetical arithmetic separately from implemented driver/default behavior.

## 63 Replication and backup

Replicas can tolerate certain node failures but propagate logical deletions, application errors and undesirable state. Recovery requirements still need backups; replication is not a substitute.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A useful backup is recoverable independently of the current replica set and tested against the required recovery point. The allocator and obfuscation settings must also agree with restored mappings. Replicating a bad upsert preserves the bad state. Follow-up: Is copying a live data directory a demonstrated safe backup? No. A datastore-specific consistent procedure and restore test are needed; this documentation review did not inspect data, make backups or measure RTO/RPO.

## 64 AOF and backup

AOF is Redis persistence/restart reconstruction, not a complete backup/disaster-recovery plan or failover mechanism.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** appendonly plus everysec records the Redis mutation stream with its own flush window. It cannot reconstruct Cassandra mappings or infer whether their maximum ID exceeds the restored counter. Coordination across backup timestamps is the unresolved boundary. Follow-up: Can restoring an old AOF alone be dangerous? Yes, if Cassandra retains newer IDs; creation can reuse them. No automatic high-watermark reconciliation tool is present.

## 65 Bilingual documentation

English supports international presentation; Brazilian Portuguese supports detailed study. Both should describe the same technical facts without invented features or metrics.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Equivalent paths and numbering allow a learner/reviewer to compare one technical contract across languages. Local link/anchor/parity validation detects structure but cannot judge translated meaning. Follow-up: How keep shared facts consistent? Review source once, propagate current mechanisms/limits to project and library, and distinguish historical evidence. Replacing one language with shorter link-only answers would lose the interview substance even if link checks passed.

## 66 Diagrams

Component and creation/resolution diagrams communicate relationships more efficiently than code alone when they add understanding. Mermaid is useful here, not a decoration requirement.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A creation sequence should show allocation before mapping and the lack of a shared commit; a resolution sequence should omit Redis. Those omissions are meaningful engineering facts. A diagram joining the portfolio to a broker would be false without code evidence. Follow-up: What makes a diagram drift-resistant? Keep it adjacent to the mechanism, use a small number of real components and update it when contracts change. No decorative performance/topology claims are needed.

## 67 Project quality

Call it an engineering/system-design portfolio with explicit decisions and limits, rather than production-ready. Single Redis, incomplete production observability/deployment and limited real-infrastructure evidence remain.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Quality here means a defendable contract and explicit limitations rather than stack size. Public API behavior, failure translation and resource lifecycle can be assessed from code/fakes while recovery/HA need new evidence. Follow-up: What would invalidate a production-ready claim? Uncoordinated allocator loss, no verified restore/failover/TLS/abuse controls and no representative load data. Documentation must keep those gaps visible rather than hide them behind a technology list.

## 68 Another week

Prioritize isolated real-service integration/failure scenarios or load measurements. Use observed latency/throughput to justify caching, allocator changes or other optimizations instead of adding technologies for appearance.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** A valuable experiment would target one invariant, such as no mapping overwrite after simulated counter loss in isolated stores, or ambiguous-write recovery. It must define fixture ownership/cleanup before touching infrastructure. Performance work needs units/environment and correctness checks. Follow-up: Are these tasks already done because they are suggested? No. They remain hypothetical priorities and must be separately authorized outside this documentation-only task.

## 69 Assessing architecture

Check clear responsibilities, genuine requirements/learning goals, known failures/trade-offs, testability, documentation accuracy and explainability. Technology count does not determine quality.

**Mechanism, trade-off and follow-up (static review; alternatives are hypothetical):** Trace normal behavior, then ask what changes when a dependency fails or state is restored inconsistently. If the answer depends on an invented transaction, consistency level or integration, the architecture explanation is wrong. A smaller SQL design can be reasonable without erasing this distributed-learning design. Follow-up: Does more documentation prove implementation completeness? No; code, assertions and dated runtime evidence establish different facts. This library explicitly marks missing workflows and unmeasured outcomes.

## 70 About sixty seconds

A Python/FastAPI shortener uses authenticated validated POST, atomic Redis integer allocation, Base62 and reversible seven-character obfuscation, then Cassandra mapping persistence. Public GET reverses to an integer, performs key lookup and responds 301. Docker-first local Redis AOF and three RF=3 Cassandra peers support study; seed is not leader. There is no Redis failover or production benchmark. Partial failures and trade-offs are explicit rather than hidden behind extra infrastructure.

## 71 About thirty seconds

A backend/system-design portfolio using Python, FastAPI, Redis and Cassandra. Atomic IDs become seven-character public codes through Base62/reversible obfuscation; three local Cassandra peers persist mappings. The study covers concurrency, distributed storage, replication, failures, HTTP semantics and simplicity/availability/consistency trade-offs.

## 72 Decision matrix

| Decision | Benefit | Cost or limitation |
| --- | --- | --- |
| Python/FastAPI | Small API/new-ecosystem learning | New stack to master |
| Redis INCR/AOF | Atomic allocation/restart durability | Central writes, no failover |
| Cassandra/three peers/RF=3 | Distributed persistence and cluster learning | Operational complexity/shared host/backup still needed |
| Base62/reversible transform | Compact URL-friendly hidden sequence | No strong cryptographic protection |
| Seven-character codes | 62^7 mathematical domain | No measured operational capacity |
| 301/public GET | Shareable permanent links/cache opportunity | Mutable destination and abuse concerns |
| Basic Auth POST | Simple creation protection | TLS needed/no complete product identity |
| Fakes | Fast deterministic application tests | No real-driver/cluster proof |
| Compose/modular service | Reproducible simple local operation | No independent domain deployment/production orchestration |
| No GET cache/broker | Fewer responsibilities | Direct Cassandra reads/no async analytics |
| No deduplication/TTL | Simple permanent write path | Repeated URLs/new IDs/no expiry |

## 73 Claims to avoid

Prefer Cassandra's learning/key-lookup fit to superiority over PostgreSQL; atomic allocation to “never loses IDs”; AOF durability to failover; seed discovery/per-request coordinator to leader; encoding/obfuscation to encryption; mathematical code domain to trillions of stored URLs; same-host cluster study to HA; fake contracts plus separate integration to universal infrastructure proof; a modular service to invented microservices best practices.

## 74 Reasoning checklist

Problem → requirement → alternatives → choice → guarantee → cost → possible failure → current treatment → remaining limitation → production change. Reasoning is more useful than memorized answers.

## 75 Interview principle

A mature answer explains why a choice fits this project's goals, the problems it solves, costs it introduces and conditions that would warrant alternatives. Demonstrate system understanding, responsibility boundaries, distributed-systems distinctions, honest measurements and transferable learning. Do not try to prove every choice uniquely correct or the architecture perfect.

## Source-grounded follow-ups and study order — 2026-10-09

The [authoritative architecture](../architecture/overview.md) documents two implementation limits: literal `0` padding assumes a zero-first alphabet, and the Redis generator does not reinitialize after losing its counter key in an already-initialized process. Helpers use global settings even when the service has injected settings. These are static findings, not executed regression results; no application tests ran in this audit.

**Question: Does a custom alphabet automatically work?** Model answer: “Validation accepts 62 unique characters, but fixed `0` padding can represent a nonzero digit or invalid character. I would retain the default alphabet and treat generalized padding/versioning as a separate code change, with round-trip tests.”

**Question: Are ID gaps and reuse equivalent?** Model answer: “Allocation followed by persistence failure consumes an ID and leaves a gap. Losing allocator state while mappings survive can reuse an ID and overwrite its Cassandra mapping. The latter is a correctness issue; AOF and the local initialization lock do not create a cross-store recovery protocol.”

**Deeper questions:** What happens if a counter key disappears after `_initialized=true`? Why can injected service Settings differ from helper settings? How would you preserve old links while rotating codec configuration? What does a fake counter test prove about live Redis concurrency?

Study order: HTTP/authentication and payload validation → service flow → Base62/modular inverse with the default alphabet → Redis initialization and failure windows → Cassandra lookup/replication versus consistency → lifespan/configuration → fake tests versus real dependency evidence → recovery alternatives and HTTP cache semantics. This is suggested study, not completed progress. Alternatives discussed for learning were not necessarily evaluated during development.

## Literal examples from the study notes

The following literal snippets retain commands, configuration, identifiers, pseudocode and placeholder values. Labels/comments inside snippets remain as originally written; explanation is in the English topics above.

```text
route
→ controller
→ service
→ infrastructure
```

```text
POST /urls
→ Basic Authentication
→ validação da URL
→ Redis INCR
→ ID inteiro
→ Base62
→ obfuscação reversível
→ código público de 7 caracteres
→ persistência no Cassandra
→ 201 Created
```

```text
62^4 = 14.776.336
```

```text
14.776.335
```

```text
14.776.336
```

```text
Redis INCR → ID 100
Cassandra → grava ID 100
```

```text
Redis gera 100
Cassandra falha
próxima requisição:
Redis gera 101
```

```text
0-9
A-Z
a-z
```

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

```text
integer
→ Base62 encode
→ Base62 decode
→ mesmo integer
```

```text
14.776.336
14.776.337
14.776.338
```

```text
62^7 = 3.521.614.606.208
```

```text
ID conhecido
→ lookup por primary key
→ URL original
```

```text
Qual seria a solução mais simples para uma aplicação pequena?
vs.
Que tecnologia permite explorar os problemas de engenharia que quero estudar?
```

```text
CREATE TABLE urls_by_id (
    id bigint PRIMARY KEY,
    original_url text
);
```

```text
ID inteiro
→ original_url
```

```text
short_code
→ desfaz obfuscação
→ Base62 decode
→ integer ID
→ Cassandra lookup
```

```text
cassandra-1
cassandra-2
cassandra-3
```

```text
seed → descoberta do cluster
coordinator → coordenação de uma requisição específica
replica → nó que possui uma cópia daquele dado
leader → conceito que não descreve a arquitetura Cassandra desse projeto
```

```text
GET /{short_code}
→ validação
→ desfaz obfuscação
→ Base62 decode
→ ID inteiro
→ Cassandra lookup
→ URL original
→ 301 Moved Permanently
```

```text
abc1234 → example.com
```

```text
Quero validar minha lógica?
ou
Quero validar a integração real com a infraestrutura?
```

```text
POST
→ Redis necessário
```

```text
GET
→ Cassandra
```

```text
integer
→ Base62
→ código público
```

```text
persistência ≠ alta disponibilidade
replicação ≠ backup
seed node ≠ leader
coordinator ≠ leader
Base62 ≠ criptografia
obfuscação ≠ criptografia
atomicidade ≠ fila
Docker containers ≠ infraestrutura de produção
testes com fake ≠ teste real de integração
arquitetura escalável ≠ throughput comprovado
```

```text
floor(RF / 2) + 1
= floor(3 / 2) + 1
= 2
```

```text
cada componente possui uma responsabilidade clara;
as decisões resolvem requisitos reais ou objetivos explícitos de aprendizado;
os principais failure modes são conhecidos;
os trade-offs são compreendidos;
o código consegue ser testado;
a documentação corresponde ao comportamento;
e eu consigo explicar por que cada componente existe.
```

```text
Qual era o problema?
        ↓
Qual requisito eu precisava atender?
        ↓
Quais alternativas existiam?
        ↓
Por que escolhi esta?
        ↓
O que ela me oferece?
        ↓
O que ela me custa?
        ↓
Como ela pode falhar?
        ↓
Como o projeto trata essa falha hoje?
        ↓
Qual limitação continua existindo?
        ↓
O que eu mudaria em produção?
```

## Additional source-grounded interview deep dives

Original questions and answers above are preserved. IDs below identify this additional sequence; they do not renumber the retained material. Levels guide rehearsal, not implementation status. Follow-ups include answers so this sequence is self-contained.

### Q001 — Intermediate: Why is the local initialization lock insufficient to guarantee globally unique IDs?

**Answer:** Implemented: a Lock protects one generator's double-checked `_initialized` flag. Across processes, Redis SET NX protects initialization and INCR serializes allocation at the shared server. The lock alone cannot coordinate other processes; server-side operations supply that boundary. Even successful atomic allocation depends on preserved counter state: AOF everysec may lose recent increments under failure, and a reset counter can reuse IDs whose mappings still exist in Cassandra. Cassandra INSERT is an upsert, so ID reuse can overwrite a destination rather than report a collision.

Follow-up: Does NX repair a deleted counter after initialization? The cached flag can skip initialization, and INCR on a missing key starts again. There is no coordinated recovery check. Follow-up: What alternative reduces this coupling? A single SQL store with generated identity and mapping in one transaction would simplify local atomicity; random codes need collision resolution, distributed IDs need clock/node discipline. Those are alternatives, not delivered migrations. Unique generation during healthy operations and safe recovery after state loss are different engineering claims.

### Q002 — Challenging: How do you classify failure after allocation or after a timed-out Cassandra write?

**Answer:** Implemented: creation first allocates, then encodes/obfuscates, then stores. A later failure consumes the integer. If Cassandra definitely did not write, there is an unused gap; if it accepted a write but the response was lost, the mapping may exist despite a 503. The service does not reconcile that ambiguity or reuse the allocated ID for a retried HTTP request. A retry allocates another ID and can duplicate the logical request. Theory: operation result and response delivery are separate events; timeout is not proof of rollback. Redis and Cassandra do not share a transaction here.

Follow-up: Would blindly retrying an upsert with the same ID be safe? Only if ownership of that ID and identical intended destination are guaranteed; the current HTTP API does not retain that context. Follow-up: What would an idempotency key require? A durable request-key/result record, payload conflict policy, concurrent-request arbitration, expiry and replay behavior, not just a header. A single-store transaction is a simpler alternative for this scale. These are hypothetical designs; no exactly-once creation or consumer-style deduplication is implemented.

### Q003 — Challenging: Why does SHA-256 parameter derivation not make the code encrypted?

**Answer:** Implemented: the code maps an integer by `(a*x+b) mod 62**7`, choosing a coprime multiplier and deriving parameters with SHA-256. Coprimality supplies reversibility and avoids collisions within the supported space for fixed settings; hashing parameters does not change the affine map into secure authenticated encryption. Codes carry no integrity tag or access policy. Resolution is public. Theory: encoding changes representation, obfuscation reduces obvious sequencing and encryption needs a defined security construction and key lifecycle. Basic authentication protects creation, not code secrecy, and requires transport protection in public deployment.

Follow-up: Can the key be rotated transparently? No version is stored in the code or mapping; decoding with a new key changes the lookup. Follow-up: What about alphabet customization? Base62 accepts 62 unique characters but padding is literal `0`, which may not be the zero digit or even belong to that alphabet. Compatibility beyond the default remains an explicit gap. A versioned stored-code scheme could support migration at storage/query cost. It is hypothetical; never treat a code as a bearer credential for private resources.

### Q004 — Intermediate: What can RF=3 and quorum reasoning tell us about this actual deployment?

**Answer:** Implemented: local bootstrap configures three Cassandra peers and RF=3; the execution profile chooses local-DC-aware routing but does not explicitly set read/write consistency. Replication factor describes desired copies, not how many acknowledgements every request waits for, and the nodes share one local host. A seed is discovery infrastructure rather than a leader. General theory: with consistent replica sets, R+W>N gives read/write quorum overlap, but conflict resolution, concurrent writes, failure detection and the precise consistency policy still matter. It is not universal linearizability or a substitute for understanding the locked driver defaults.

Follow-up: Can we promise immediate successful resolution after creation solely from RF? No project-owned read-after-write guarantee is established by that setting. Follow-up: Are replicas backups? No; deletion/corruption can propagate, and host loss can affect all local nodes. Real replication/failure and backup-restore tests remain gaps. Choosing explicit quorum could make the contract more deliberate at latency/availability cost, but no configuration change or cluster execution occurred in this documentation task.

### Q005 — Introductory: How do API status, health and tests differ as evidence?

**Answer:** Implemented: authenticated valid POST succeeds with 201; public GET returns 301, invalid/missing codes 404, configuration failures 500 and adapter failures 503. A permanent redirect can be cached, so application logs do not measure every later visit. The Compose app probe requests OpenAPI after startup; startup initializes Cassandra, while Redis allocation is lazy. Thus a green probe does not prove a fresh Redis increment or mapping lookup. GET's dependency path excludes Redis, but app restart still depends on Cassandra initialization.

Follow-up: Do fake HTTP/service tests prove the real cluster works? No; they verify validation, mapping and call ordering under modeled outcomes. Driver defaults, authentication, actual partial writes and failover require isolated infrastructure tests. Follow-up: What would production observability add? Per-operation latency/error categories, dependency readiness and counter recovery alarms without leaking credentials/destinations. Those are hypothetical. Local reload, bind mounts and health probes do not constitute a production deployment strategy; retention, consistent restoration and rollback remain evidence-dependent gaps.

## Source reconciliation — 2026-10-18

`40e4ea05d6e4d2d5ae81d2020ec6ea7936330d44`. The source, API/CLI entry points, persistence/resource boundaries and test definitions were reviewed statically. The existing explanations and interview answers remain applicable within their recorded limits. No runtime test results were produced. See the project’s standalone [implementation and interview path](../guides/implementation-study.md).
