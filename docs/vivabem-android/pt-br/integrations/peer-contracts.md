# Fronteiras de integração — VivaBem Android

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

VivaBemFirebaseMessagingService diferencia display/cancel, correlaciona tags/IDs, verifica permissão e cria PendingIntents imutáveis via trustedUri. onNewToken grava last_token em preferências privadas; essa escrita não prova registro no servidor. A entrada web e OfficialAppRequestDetector do Portal determinam autenticação app. RedisAuthenticationSession do Portal usa inatividade móvel de 60 dias, separada da duração do cookie e de presença/push passivos.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [VivaBem](../../../vivabem/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
