# Hub backend tests and execution limits

[Contents](../index.md) | [Português brasileiro](../../pt-br/operations/backend-testing.md)

Reviewed 2026-11-10 at `2338ad3`. Audience: Node maintainers and security reviewers. Source assertions are distinguished from executed results; no test or runtime was changed.

<!-- reading-section: runner -->
## Runner and isolation

`node-server/package.json` defines npm test as `node scripts/run-tests.mjs`. The runner discovers ordinary .test.js/.mjs/.cjs files under tests/node-server, sorts them and invokes the current Node executable with --test and TAP output. Empty discovery, execution failure or zero reported tests fail the command. It is not the obsolete single contratos-backend.test.mjs suite.

Tests import focused modules rather than starting server.js. They use synthetic in-memory sockets/Redis/probe adapters; configuration fixtures create and remove owned temporary files. Publisher tests use real jose-generated ephemeral RS256 keys and signed tokens in memory. Thus cryptographic assertions exist in source even though this session could not execute them. No live Redis, broker, recipient website or production signing keys are required by these cases.

<!-- reading-section: modules -->
## Current test modules

| Existing file | Assertions |
| --- | --- |
| `tests/node-server/aplicacao.test.mjs` | Public Socket.IO publish handler, denied/failed ACKs, HTTP liveness/404, readiness and subscription retry |
| `tests/node-server/configuracao.test.mjs` | Environment validation, mandatory patterns, bounded ACL roles, policy fixtures and empty-runner rejection |
| `tests/node-server/publicadores.test.mjs` | Actual RS256/jose verification, issuer/audience/subject/scope/time/type/kid, channel/event/transport policy |
| `tests/node-server/destinatarios.test.mjs` | Exact origin/cookie, no redirects, malformed probe identity, revalidation, private token removal and professional-only delivery |
| `tests/node-server/roteamento.test.mjs` | Envelope identity, allowed routes/audience, payment correlation, signed-body tampering and dedicated Node transport |

Nested subtests/data-driven cases make source file counts different from reported runtime counts. Do not retain the previous nine-case statement as the current result.

<!-- reading-section: execution -->
## Actual attempt

Working directory node-server:

```sh
node scripts/run-tests.mjs
```

Actual exit 127: node was not found on the host. No test count or passing result was observed. npm test is the package alias, not a second suite. No container was started or dependency installed to disguise this limitation. Run the existing command under the approved Node 22 runtime with installed lockfile dependencies when available.

<!-- reading-section: limits -->
## Operational meaning and maintenance

Source assertions do not certify live Socket.IO handshake/housekeeping, Redis reconnect, effective ACL rollout or recipients across browser sessions. Ready requires connected publisher/subscriber and completed subscriptions; liveness alone does not establish readiness. A publish ACK follows Redis publish acceptance, not recipient receipt. Pub/Sub has no durable replay/deduplication guarantee; domain applications own authoritative rereads and financial recovery.

Sources: node-server/scripts/run-tests.mjs, package.json, src/aplicacao.js, src/assinaturas.js, src/envelopeRedis.js, src/roteamentoDestinatario.js and the five test files above. Update both languages and the curated collection when handlers, policies, dependencies or test discovery change. New tests/infrastructure remain outside this documentation task.
