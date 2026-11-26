# FAQ técnica — Hub VivaBem

[English](../../en/faq/index.md) | [Português brasileiro](index.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: q001 -->

## Q001 — /ready comprova funcionamento do ecossistema?

Não. Observa clientes Redis, assinaturas iniciais e shutdown. Não certifica RabbitMQ, disponibilidade da autorização Portal para cada destinatário, entrega ao navegador, bancos ou execução financeira. Liveness é verificação ainda mais restrita do processo.

<!-- reading-section: q002 -->

## Q002 — Um publisher pode receber todos os eventos do navegador?

A credencial de publicação não concede recepção. Destinatários usam identidade de sessão Portal validada separadamente e roteamento específico. ACK de publicação também não comprova que o destinatário estava conectado.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem validação?

ACLs efetivas, overlays/bindings de produção, certificados/TLS, persistência/recuperação de brokers, fanout para clientes lentos e capacidade permanecem sem validação. Readiness Node não certifica fluxos AMQP. Nenhum teste de transporte ou comando de broker foi executado.

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Failure scenarios / Cenários de falha](failure-scenarios.md)
