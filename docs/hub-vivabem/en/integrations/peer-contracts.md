# Integration boundaries — Hub VivaBem

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

GET /health reports process liveness; /ready returns 200 only after initial subscription ACKs and with both Redis clients ready and no shutdown, otherwise 503. POST /events is absent and falls through to 404. Socket.IO uses /socket.io/. publish_event acknowledgements distinguish unauthorized, redis_unavailable and rejected input from successful Redis publication; none proves browser receipt or durable domain processing. Required direct subscription patterns must appear literally: a broader wildcard is not accepted as equivalent coverage.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
