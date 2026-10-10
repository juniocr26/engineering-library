# url-shortener: implementation dossier

[English](url-shortener.md) | [Português brasileiro](../../pt-BR/architecture/url-shortener.md)

Static review: 2026-10-10. This independent portfolio project has no verified runtime calls to another portfolio repository. Evidence links support the complete explanations below.

## Creation and redirect contract

`POST /urls` requires HTTP Basic credentials and a Pydantic `HttpUrl` JSON field `url`; success is 201 with `short_code` and `short_url`. The route calls a controller, which delegates to `UrlShortenerService`. The service allocates an integer, encodes Base62, applies reversible obfuscation, stores `(id, original_url)` in Cassandra, and constructs the public URL from `SHORT_URL_BASE`. Input validation checks HTTP/HTTPS syntax; it does not fetch the destination, prove it is reachable or classify abuse. Repeated URLs produce distinct IDs rather than deduplicated records.

`GET /{short_code}` is public. It requires exactly seven characters for deobfuscation, reverses to the integer, looks up Cassandra and returns 301 with Location. Invalid code and absent mapping both become 404. Configuration errors become 500; Redis/Cassandra adapter errors become sanitized 503. Redis is absent from the resolution path, so a healthy initialized app may still resolve while Redis is down. Cassandra is required for both paths. Startup creates a Cassandra session and ensures the mapping table; a running health probe against OpenAPI does not test a fresh mapping lookup or counter increment.

This is a synchronous API with synchronous dependency clients; declaring an async route would not make those calls nonblocking. Permanent redirects may be cached by browsers/intermediaries and later redirects can bypass the application, so future click analytics would not necessarily see every visit. There is no expiration, editable destination, abuse moderation, rate limit, idempotency key or analytics endpoint. Changing these contracts requires design and tests rather than inferring them from the domain name.

## Identity, mappings and consistency

Redis `SET NX` initializes the shared counter to start minus one; `INCR` allocates an integer atomically at the server. The process lock and `_initialized` flag avoid redundant initialization within one generator, while NX handles competing initializers across processes. Neither the lock nor INCR creates a transaction with Cassandra. Cassandra `urls_by_id` uses `id bigint PRIMARY KEY` and `original_url text`; inserts and reads use bound values. The table is query-shaped for single-key resolution rather than joins or search by destination.

If allocation succeeds but storage fails, the ID is consumed. A timeout after Cassandra accepted the write may leave a mapping even though the caller sees failure. Retrying creation allocates another ID. Gaps are harmless if allocation never reuses an existing ID, but losing/resetting counter state while mappings survive can overwrite a row because INSERT is an upsert. Redis AOF `everysec` is configured locally; it is neither zero-loss durability nor coordinated backup of both stores. Restoration requires a counter floor consistent with retained mappings, plus preserved alphabet/key compatibility. The application has no automated repair/recovery coordinator.

The Compose/bootstrap design has three Cassandra peers and NetworkTopologyStrategy RF=3. All are local; they do not represent three independent host failure domains. Seeds assist discovery, not leader election. `DCAwareRoundRobinPolicy` sets local-DC preference but no read/write consistency is explicitly selected in the execution profile. Do not derive a guaranteed read-after-write contract from RF alone. Quorum reads/writes are a hypothetical alternative that trade replica acknowledgements and availability for stronger overlap; conditional writes would address a different invariant and add coordination cost.

Encoding an integer takes repeated divmod by 62; seven-character obfuscation operates modulo `62**7`. SHA-256 derives affine parameters, `gcd(a, modulus)=1` enables a modular inverse, and padding gives fixed width under the default alphabet. The counter can outgrow this space; the service then returns a configuration error after consuming an ID. A non-default alphabet has an additional unresolved compatibility concern: padding is literal `0`, which need not represent digit zero. Treat arbitrary alphabet changes as unverified, not transparently supported migrations.

## Authentication, obfuscation and transport

HTTP Basic checks configured username and password using `secrets.compare_digest`. Invalid credentials return 401 with a Basic challenge; missing configuration returns 500. Basic credentials are an encoding, not transport encryption. The local application does not configure TLS termination. The public redirect route is intentionally unauthenticated, and possession of a short code is not an authorization check. CORS or a private Compose network would not substitute for API authentication.

The affine transformation is reversible obfuscation, even though SHA-256 derives its parameters. It is not authenticated encryption, a password hash or a secrecy boundary. Known input/output pairs and its algebraic structure make cryptographic-security claims inappropriate. Changing the key or alphabet changes decoding of existing links; there is no version prefix or migration lookup. A random stored code would avoid coupling decoding to one global key but require collision handling and another query key; authenticated encryption would introduce different length/key-management requirements. Neither is implemented.

Destination syntax is validated, but no allowlist or reputation check exists. The app redirects rather than fetching URLs, so its current creation path is not a server-side URL fetcher; a future preview/fetch feature would create new SSRF concerns. Avoid logging credentials or full sensitive destinations. Real environment files and datastore contents were not read. Security gaps include TLS deployment, abuse controls, credential rotation procedures and tested code/key migration.

## Deployment and coordinated recovery

Lifespan creates Redis and Cassandra resources, ensures the table and exposes adapters on application state. Cassandra initialization occurs before serving; Redis counter initialization is lazy. `finally` closes Cassandra resources and Redis; failed Cassandra connection creation shuts down the cluster. The default Compose command is Uvicorn with reload, intended for local development. Three Cassandra nodes, Redis AOF storage and bind mounts are a learning topology, not a verified production HA release.

Update/rollback review must preserve database contents and the code-space contract. Never reset Redis independently of Cassandra mappings or assume recreating containers recreates credentials in initialized volumes. Back up and restore both stores coherently and retain obfuscation settings; volume persistence is not backup. These are procedure requirements, not a restore rehearsal performed here. No coordinated recovery tool, application release pipeline or measured RTO/RPO is present. There is no schema-versioned destination-edit lifecycle.

Fake tests isolate encoding, allocation, service ordering and HTTP error mapping without proving real cluster consistency, authentication or failover. Existing Docker/Postman instructions are unexecuted during this review. OpenAPI reachability proves HTTP startup, not dependency readiness at request time. Potential performance costs are synchronous network calls, Redis serialization, Cassandra replica/network work and client thread capacity; no throughput chart can be derived from topology. Remaining gaps include real failure injection, counter-loss recovery, concurrent load, quorum policy selection and deployment/rollback exercises.

## Supporting evidence

- [api/contracts](../../../../url-shortener/docs/en/api/contracts.md)
- [database/identity-and-consistency](../../../../url-shortener/docs/en/database/identity-and-consistency.md)
- [security/identity-and-transport](../../../../url-shortener/docs/en/security/identity-and-transport.md)
- [operations/deployment-and-recovery](../../../../url-shortener/docs/en/operations/deployment-and-recovery.md)
- [Interview / Entrevista](../interviews/url-shortener.md)
