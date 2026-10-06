# URL Shortener technical interview study guide

[English](url-shortener.md) | [Português brasileiro](../pt-BR/url-shortener.md)

Study the problem, choices, alternatives, trade-offs and production limitations rather than memorizing answers. First-person wording should reflect experience you can substantiate. Repeated explanations from the original notes are consolidated; literal examples remain in the appendix. Paths/commands refer to the `url-shortener` repository.

Code review corrections: Redis counter initialization is lazy on first ID generation, not in lifespan. Lifespan issues Cassandra CREATE TABLE IF NOT EXISTS; Compose bootstrap can create/alter roles/keyspace. Startup is a write operation, not a harmless check against existing data. There is no TTL, deduplication or conditional-insert protection against ID reuse. Configuration errors can become 500, distinct from infrastructure 503; invalid payloads produce 422. No explicit QUORUM level is selected in the current execution profile; QUORUM discussion below is a hypothetical design choice.

## 1 Overview

The project is a Python/FastAPI URL shortener for backend engineering and system-design learning. Authenticated creation validates a URL, allocates an integer via Redis INCR, encodes Base62, applies reversible obfuscation to form a seven-character code, and persists integer-to-URL mapping in Cassandra. Public resolution reverses the transform, decodes the integer, queries Cassandra and returns 301 Moved Permanently. Local Docker infrastructure includes Redis and three Cassandra nodes.

## 2 Why this problem

A small API exposes meaningful questions about unique IDs, concurrency, persistence, compact representations, distribution, durability, availability, HTTP caching and redirects. The goal is a system whose entire flow and trade-offs can be understood, not technology quantity.

## 3 Components

FastAPI handles HTTP; Redis allocates IDs; Cassandra persists mappings; Base62 represents integers; reversible transformation hides the obvious sequence; Compose reproduces local infrastructure; Pytest tests behavior. Cassandra is peer-to-peer: cassandra-1 is a discovery seed, not a leader/master.

## 4 Python FastAPI and architecture

Python was deliberate hands-on learning in another backend ecosystem. Work mainly coordinates validation and infrastructure rather than heavy compute. Transferable engineering reasoning is distinct from new language/framework syntax. FastAPI provides HTTP, data validation and OpenAPI while route → controller → service → infrastructure keeps responsibilities visible. This is pragmatic layering, not a complete rigid Clean Architecture implementation; more interfaces/repositories need actual benefits.

## 5 Creation flow

POST /urls → Basic Auth → URL validation → Redis INCR → integer → Base62 → reversible obfuscation → seven-character code → Cassandra persistence → 201 Created. Creation changes state, so it is authenticated. Each valid POST allocates another ID; no original-URL deduplication or TTL is implemented.

## 6 Redis responsibility

Redis is the atomic ID allocator, not the mapping database, GET cache or message queue. INCR handles concurrent increments. SELECT MAX(id)+1 would race when two requests observe the same maximum and is not the intended Cassandra global-counter model. Atomicity does not require manually queueing requests.

## 7 Counter initialization

Default first intended ID is `62^4 = 14,776,336`. SET with NX initializes the counter to 14,776,335 only if absent; the first INCR returns 14,776,336. Existing persisted state is not overwritten by initialization. This happens lazily on first generation, with a local lock around initialization.

## 8 Why start at that value

With the chosen alphabet, 62^4 encodes as `10000`, selecting a desired Base62 range before transformation. This is a project choice, not a fundamental shortener requirement.

## 9 Redis durability and availability

AOF with appendfsync everysec improves restart recovery but does not implement failover. There is one Redis, no Sentinel/Cluster. Redis failure blocks new creation with infrastructure error; durability is different from HA.

## 10 Partial failures across two stores

Redis allocation precedes Cassandra persistence without a shared transaction. If persistence fails, a sequence gap is acceptable: uniqueness matters, gaplessness does not. If Redis loses acknowledged increments but Cassandra retains their mappings, IDs can be reused. Cassandra's ordinary insert can replace a mapping, making this a correctness risk. AOF reduces risk without fully solving recovery; production ID guarantees need review.

## 11 Base62

Alphabet: `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. It compactly represents integers using URL-friendly alphanumerics. Encode/decode returns the same integer. It is neither encryption nor Base64 and offers no confidentiality.

## 12 Obfuscation and code space

Plain Base62 exposes sequential progression. A reversible transform hides the obvious sequence and yields fixed seven-character codes; it is not strong cryptography. A cryptographic requirement needs an appropriate reviewed construction. `62^7 = 3,521,614,606,208` possible codes is a mathematical domain, not measured capacity for trillions of stored URLs.

## 13 Cassandra versus a simpler database

Known integer → primary-key lookup → original URL fits query-driven modeling. Cassandra supports study of replication, peers, seeds and coordinators. It is not mandatory for a small shortener; PostgreSQL could be operationally simpler. Distinguish the simplest small-product design from a technology selected for explicit distributed-storage learning.

## 14 Data model

```sql
CREATE TABLE urls_by_id (
    id bigint PRIMARY KEY,
    original_url text
);
```

Resolution needs no joins. Public code is not the primary key because it reversibly maps through Base62 back to the integer. Persistence keeps that integer identity independent of its public representation.

## 15 Seeds coordinators and replicas

No permanent leader exists. cassandra-1/2/3 are peers. Seed means bootstrap discovery; coordinator means the node managing one request; replica means a node storing a copy. Another request can have another coordinator. None of these roles should be described as a permanent leader.

## 16 Replication factor

NetworkTopologyStrategy with RF=3 in datacenter1 replicates rows among the three local nodes. This alone is not end-to-end HA: consistency levels, client availability, topology, deployment, failure detection and operations matter. All three development containers share one physical machine and fail with that host.

## 17 Consistency levels

Choose per-operation read/write guarantees after defining failure, latency and availability requirements. With RF=3, QUORUM is one option, not automatically best. Current driver execution profile does not explicitly choose QUORUM; the study discussion is a proposed review rather than implemented configuration.

## 18 Resolution flow

GET /{short_code} → validate/reverse obfuscation → Base62 decode → integer → Cassandra lookup → original URL → 301. It is public so shared links do not require recipients to authenticate.

## 19 Permanent redirects

301 matches permanent mapping semantics and may be cached by browsers/proxies, reducing future backend requests. That benefit also means editing a server mapping may not update clients with cached old destinations. Mappings are effectively immutable in the application; there is no edit endpoint. A temporary redirect such as 302 merits review for mutable destinations or request-level analytics. Cache behavior varies and is not a capacity guarantee.

## 20 Why no Redis GET cache

Redis currently has one clear responsibility. Resolution caching would add invalidation, eviction, memory, misses, consistency and failure behavior. Introduce it when read measurements or an explicit study requirement justify it, not merely because Redis exists.

## 21 Why no broker

Creation returns the code immediately through a short synchronous flow. Kafka/RabbitMQ would add producers, consumers, retries, idempotency, delivery and eventual consistency without a current requirement. Analytics/auditing/post-processing or decoupled integrations could justify asynchronous work later.

## 22 Why one service

The small domain lacks independent contexts or operation needs requiring separate deployments. A modular service is easier to run/test/explain. Microservices would introduce communication, observability, retry and partial-failure costs before a corresponding requirement.

## 23 Basic Authentication

Basic Auth protects POST while GET remains public, keeping identity outside the main study scope. Credentials are transport-encoded rather than protected by encryption; production requires HTTPS. `secrets.compare_digest` supports comparison, and real credentials must not be committed. Multiuser product identity could need tokens or an identity provider; Basic Auth here is not that complete architecture.

## 24 Secrets

`.env.example` is public configuration structure; real Redis/Cassandra passwords, Basic Auth credentials and OBFUSCATING_KEY belong in ignored local configuration or appropriate infrastructure secret storage. Production secret management is a separate concern.

## 25 Connection lifecycle

FastAPI lifespan constructs Redis, ID generator and Cassandra cluster/session for reuse, closing resources on shutdown. Per-request Cassandra sessions would be costly. Lifespan also initializes the URL table, so startup can write schema even before HTTP writes.

## 26 Docker-first operation

Docker/Compose, an editor and Git reproduce Python/Redis/three Cassandra nodes without installing each runtime on the host. Three same-host Cassandra containers demonstrate logical cluster topology, peers and replication, not independent physical failure domains or production HA.

## 27 Readiness

Compose health checks and dependency conditions express readiness instead of arbitrary sleeps. Service startup time varies. Application health queries OpenAPI and is not a full production dependency/observability guarantee. Startup hooks must be reviewed for schema and role writes before using an existing database.

## 28 Tests

Pytest covers HTTP authentication/redirects, creation/resolution, Redis allocation behavior, Cassandra store behavior, Base62 and reversible transforms. The standard suite uses fakes. These deterministic tests establish application contracts, not all real-cluster behavior. Infrastructure integration needs separate isolated validation.

## 29 Why fakes

Encoding, input validation, authentication and service behavior do not need three database nodes per case. Separate logic correctness from real-driver/cluster integration; each has value and a different cost.

## 30 Dependency failures

Persistence/lookup failures map to sanitized 503 without hostnames, traces or credentials. Redis failure blocks POST; GET resolution itself needs only Cassandra. Configuration faults are distinct and can map to 500.

## 31 Availability per operation

For an already-running app with Cassandra healthy, Redis failure can block creation while existing links still resolve. Startup has stronger dependency gates, so do not confuse this read-path property with an app that always starts without Redis.

## 32 Invalid URLs

FastAPI/Pydantic validates the HTTP payload before ID allocation/persistence. Invalid payloads return 422 and avoid unnecessary infrastructure work.

## 33 Invalid codes

Malformed and unknown codes return 404; the public API does not reveal whether decoding, deobfuscation or missing mapping caused the result. Configuration/infrastructure faults are handled separately.

## 34 Repeated URLs

Two valid posts of the same URL allocate two IDs. Deduplication would require another lookup/index/mapping by original URL and concurrency rules. The current simple write path does not implement it.

## 35 Expiration

No TTL or automatic expiry. Permanent mappings avoid retention/cleanup/expired-response/cache decisions; adding expiry would introduce those requirements.

## 36 Scale claims

Atomic allocation and distributed storage permit scalability discussion, not a claim of billions of requests or measured production throughput. Define hardware, topology, consistency, load, latency and throughput before claiming capacity. “High-throughput” describes the study objective, not a demonstrated metric.

## 37 Potential bottleneck

A single global Redis allocator centralizes writes and is a single point of unavailability. Efficient INCR does not remove central dependence; higher availability/volume may justify another allocation design.

## 38 ID alternatives

UUID, UUIDv7, Snowflake-like IDs, preallocated blocks, dedicated allocation service or random IDs with collision handling each have trade-offs. Redis INCR is deterministic and easy to explain under concurrency but centralizes allocation.

## 39 Why not UUID

UUID could reduce dependence on a central counter. This project specifically studies integer → Base62 → public-code transformation and atomic allocation. Different requirements could make UUID an appropriate choice.

## 40 Observability

There is no complete production metrics/tracing/alerting stack. Potential production additions include latency/error rates, dependency availability, traces and alerts. These are limitations/future considerations, not current capabilities.

## 41 CI and deployment

Describe only checked-in workflows. Local Docker/test reproducibility does not automatically provide CI/CD, production orchestration or deployment automation.

## 42 Kubernetes

Compose meets local development/study needs. Kubernetes would add operational scope unless distributed deployment itself becomes an explicit learning/product requirement.

## 43 A startup product choice

For a small new product, PostgreSQL is a strong simple/mature/flexible option. Start from actual requirements and observed scale. Cassandra's learning and key-lookup fit does not establish universal superiority.

## 44 SQL and NoSQL

Either can support shorteners. Access patterns, consistency, scale, operations, team and infrastructure determine suitability; SQL is not incapable of this model.

## 45 Production review

Evaluate ID allocator HA/recovery, Cassandra consistency and independent failure domains, TLS, product authentication, secret management, rate limiting, observability/alerts, load and real integration tests, backup/recovery, CI/CD and malicious-URL abuse prevention. Select improvements from actual requirements rather than adding all technologies unconditionally.

## 46 Most interesting decision

Separating identity allocation from persistence clarifies responsibility but creates a distributed partial-failure problem without one transaction. Gaps, state loss and ID reuse are central learning points.

## 47 Greatest limitation

One Redis with AOF still lacks failover and can lose allocator state while Cassandra retains higher-ID mappings. Recognize correctness and recovery limitations explicitly rather than claiming persistence solves them.

## 48 Lessons

Persistence differs from HA; replication from backup; seed/coordinator from leader; Base62/obfuscation from encryption; atomicity from queues; containers from production infrastructure; fakes from real integration; potentially scalable design from measured throughput.

## 49 Honest experience

This project broadens hands-on Python/Cassandra/distributed-systems understanding; do not pretend prior professional mastery. Explain actual connection lifecycle, concurrency, persistence, replication, failures and tests separately from professional experience.

## 50 Learning a new technology

Start with its responsibility and required guarantees, then study ecosystem implementation. Cassandra understanding includes peers, seeds, coordinators, RF and operational consistency, not simply connecting a driver. This reasoning transfers between stacks.

## 51 Layer responsibilities

Route defines HTTP/dependencies; controller bridges transport/application; service coordinates creation/resolution; infrastructure encapsulates Redis/Cassandra. FastAPI permits inline logic, but visible responsibilities improve comprehension without unnecessary extra layers.

## 52 SOLID

Pragmatic separate responsibilities and replaceable dependencies improve testing. Do not present the project as a formal demonstration of all five principles or invent interfaces/hierarchies to satisfy a checklist.

## 53 Repository abstractions

CassandraUrlStore encapsulates required persistence. Multiple implementations, a richer domain or actual decoupling needs could justify a formal repository abstraction; avoid adding it everywhere by default.

## 54 Dependency injection

Construct resources in lifecycle instead of creating arbitrary infrastructure inside logic. Tests replace dependencies with fakes, permitting behavioral checks without real services per case.

## 55 Internal error details

Infrastructure exceptions are not public contracts and can leak sensitive information. Return controlled client errors; a production logging/observability policy would retain appropriate diagnostics internally.

## 56 Scaling reads

Measure first. Popular-mapping caches or HTTP/edge caches could help when justified. Immutable mappings simplify caching, but invalidation, consistency, eviction and failure still need design.

## 57 301 and capacity

Cached redirects can bypass later backend requests. Cache clearing/ignoring and varying clients prevent treating this as a guaranteed capacity solution. It complements, not replaces, planning and measurements.

## 58 Editable destinations

Reconsider redirect semantics before introducing updates. A cached 301 can retain the old destination even after a database change. Mutable mappings need explicit update modeling and suitable temporary redirects/cache policy.

## 59 Click analytics

Avoid making redirect depend on heavy synchronous analytics. Events/asynchronous processing may justify a broker only after defining acceptable loss, exactly-once expectations, volume and latency. Current code does not implement analytics.

## 60 Rate limiting

A real public API merits review of creation limits and abuse prevention. These are not currently implemented features.

## 61 CAP discussion

Do not reduce CAP to choosing two letters or label Cassandra AP without operational detail. Under partition, availability/consistency decisions depend on read/write requirements, RF and consistency levels. Discuss concrete failure behavior.

## 62 Quorum arithmetic

With RF=3, quorum is `floor(RF / 2) + 1 = 2`. Arithmetic alone does not choose per-operation guarantees or account for latency/availability. This is a hypothetical setting rather than an explicit current profile configuration.

## 63 Replication and backup

Replicas can tolerate certain node failures but propagate logical deletions, application errors and undesirable state. Recovery requirements still need backups; replication is not a substitute.

## 64 AOF and backup

AOF is Redis persistence/restart reconstruction, not a complete backup/disaster-recovery plan or failover mechanism.

## 65 Bilingual documentation

English supports international presentation; Brazilian Portuguese supports detailed study. Both should describe the same technical facts without invented features or metrics.

## 66 Diagrams

Component and creation/resolution diagrams communicate relationships more efficiently than code alone when they add understanding. Mermaid is useful here, not a decoration requirement.

## 67 Project quality

Call it an engineering/system-design portfolio with explicit decisions and limits, rather than production-ready. Single Redis, incomplete production observability/deployment and limited real-infrastructure evidence remain.

## 68 Another week

Prioritize isolated real-service integration/failure scenarios or load measurements. Use observed latency/throughput to justify caching, allocator changes or other optimizations instead of adding technologies for appearance.

## 69 Assessing architecture

Check clear responsibilities, genuine requirements/learning goals, known failures/trade-offs, testability, documentation accuracy and explainability. Technology count does not determine quality.

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
