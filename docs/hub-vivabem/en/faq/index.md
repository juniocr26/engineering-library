# Technical FAQ — Hub VivaBem

[English](index.md) | [Português brasileiro](../../pt-br/faq/index.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: q001 -->

## Q001 — Does /ready prove the ecosystem works?

No. It observes Redis clients and initial subscriptions plus shutdown state. It does not certify RabbitMQ, Portal authorization availability for every recipient, browser delivery, databases or financial execution. Liveness is an even narrower process check.

<!-- reading-section: q002 -->

## Q002 — Can a publisher receive every browser event?

No receive grant follows from publication credentials. Recipients use independently validated Portal session identity and event-specific routing. A successful publication ACK also does not prove the addressed recipient was connected.

<!-- reading-section: q003 -->

## Q003 — Which claims remain unverified?

Effective ACLs, production overlay/bindings, certificate/TLS deployment, broker persistence/recovery, slow-client fanout and capacity limits remain unverified. Node readiness does not certify AMQP workflows. No transport tests or broker commands ran.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
