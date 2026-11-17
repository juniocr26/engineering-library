# Failure reasoning — Hub VivaBem

[English](failure-scenarios.md) | [Português brasileiro](../../pt-br/faq/failure-scenarios.md) · [Index / Índice](../index.md)

Static source review: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: q004 -->

## Q004 — Where does consistency end?

Pub/Sub has no replay log for disconnected recipients. Redis transport success is not a financial commit. The event envelope carries channel/event/payload and source/project identity; direct signed publications bind the complete parsed envelope to an RS256 token. The Node namespace carries envelope plus publisherToken and uses its own authorization path. Recovery requires authorized rereads of domain state, not assumptions that every notice was retained.

<!-- reading-section: q005 -->

## Q005 — How should investigation proceed?

Read configuracao.js, politicaPublicador.js, autenticacaoPublicador.js, envelopeRedis.js, roteamentoDestinatario.js, destinatarios.js and assinaturas.js in that order. For future isolated acceptance, compare /health with /ready while Redis is unavailable, delay subscription ACKs, reconnect, revoke the Portal session and attempt delivery to another synthetic user. Real brokers/Portal and traffic budgets require separate acceptance. Do not start this repository or publish test events into shared infrastructure for documentation validation.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
