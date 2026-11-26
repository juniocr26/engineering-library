# Fronteiras de integração — Hub VivaBem

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

GET /health informa liveness do processo; /ready retorna 200 apenas após ACKs iniciais de assinatura, com ambos os clientes Redis prontos e sem shutdown; caso contrário, 503. POST /events está ausente e cai em 404. Socket.IO usa /socket.io/. ACKs de publish_event distinguem unauthorized, redis_unavailable e entrada rejeitada de publicação Redis bem-sucedida; nenhum comprova recepção no navegador ou processamento durável de domínio. Padrões diretos obrigatórios precisam aparecer literalmente: curinga mais amplo não é cobertura equivalente.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [VivaBem](../../../vivabem/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
