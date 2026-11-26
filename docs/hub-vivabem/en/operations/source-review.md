> Historical source-review record. Current contracts and verification are linked from [Architecture](../architecture/overview.md). Dates, revisions and test results below retain their original scope.

# Source review — Hub VivaBem

[English](source-review.md) | [Português brasileiro](../../pt-br/operations/source-review.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: scope -->

## Inspection coverage

Initially clean source tree. Selective static reading of the listed paths supports this collection; enumeration is not full-repository review. Symbols/consumers are identified in the chapters. No application, database, broker or deployment command ran.

<!-- reading-section: sources -->

## Source files

- `hub-vivabem/node-server/package.json`
- `hub-vivabem/node-server/src/app.js`
- `hub-vivabem/node-server/src/server.js`
- `hub-vivabem/node-server/src/config.js`
- `hub-vivabem/node-server/src/publisherPolicy.js`
- `hub-vivabem/node-server/src/publisherAuth.js`
- `hub-vivabem/node-server/src/redisEnvelope.js`
- `hub-vivabem/node-server/src/recipientRouting.js`
- `hub-vivabem/node-server/src/recipients.js`
- `hub-vivabem/node-server/src/subscriptions.js`
- `hub-vivabem/tests/node-server/subscriptions.test.js`

<!-- reading-section: history -->

## Historical reuse and corrections

The old map preserves the separation of Pub/Sub and AMQP, reread recovery and staged HUB findings. Earlier HTTP POST /events and RabbitMQ-gated Node descriptions are historical; current app.js has only /health, server.js adds /ready, and later HUB-06 records supersede the earlier gate narrative. No historical test count has been promoted to a result of this task.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/en/architecture/hub-vivabem.md`
- `engineering-library_old/docs/en/interviews/hub-vivabem-interview.md`

<!-- reading-section: access -->

## Checks and source access

Code paths are references for an authorized source checkout only. They are deliberately code spans: no private source snapshot/catalog was approved or generated, so the reader cannot expand them. Documentary navigation uses collection links. No database catalog ingestion ran. See the central review for checks actually executed.

<!-- reading-section: gaps -->

## Missing evidence and remaining work

Effective ACLs, production overlay/bindings, certificate/TLS deployment, broker persistence/recovery, slow-client fanout and capacity limits remain unverified. Node readiness does not certify AMQP workflows. No transport tests or broker commands ran.

[Library review / Revisão da biblioteca](../../../engineering-library/en/operations/vivabem-documentation-review.md)
